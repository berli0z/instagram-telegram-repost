import configparser
import json
import logging
import os
import time
from argparse import ArgumentParser
from datetime import datetime
from io import BytesIO
from os import listdir
from os.path import isfile, join, exists

import instaloader
import requests
from PIL import Image

logging.basicConfig(format='%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s', level=logging.DEBUG,
                    filename='logs.log')

# working directory path fix if run from crontab
logging.debug('Current working dir: ' + os.getcwd())
if 'instagram-telegram-repost' not in os.getcwd():
    logging.warning('Changing working directory to: ' + os.getcwd() + '/instagram-telegram-repost')
    os.chdir(os.getcwd() + '/instagram-telegram-repost')
    print(os.getcwd())
    logging.warning('Working dir changed to: ' + os.getcwd())

# define arguments
p = ArgumentParser()
p.add_argument("-c", "--config_file", default='config.conf', type=str, help='Config file')
p.add_argument("-p", "--page")
p.add_argument("-u", "--username")
p.add_argument("-k", "--password")
p.add_argument("-i", "--chat-id")
p.add_argument("-t", "--bot-token")
args = p.parse_args()

# or load arguments from configuration
if args.config_file:
    config = configparser.ConfigParser()
    config.read(args.config_file)
    defaults = {}
    try:
        defaults.update(dict(config.items("Defaults")))
    except:
        logging.warning('Cant find [Defaults] section: wrong config file path?')
    p.set_defaults(**defaults)
    args = p.parse_args()  # Overwrite arguments

# check if arguments passed correctly
try:
    PAGE = args.page
    USER = args.username
    PASSWORD = args.password
    CHAT_ID = args.chat_id
    TELEGRAM_TOKEN = args.bot_token
except:
    raise SystemExit('Arguments missing, please open README.md')


class Post:

    def __init__(self, filename, images, media_type, caption):
        self.filename = filename
        self.images = images
        self.media_type = media_type
        self.caption = caption

    def publish_in_telegram(self, token=TELEGRAM_TOKEN, chat_id=CHAT_ID):
        response = requests.post(
            url='https://api.telegram.org/bot{0}/{1}'.format(token, self.media_type),
            data={'chat_id': chat_id, 'caption': self.caption},
            files={'photo': open(PATH + '/' + self.images[0], 'rb')}
        ).json()
        time.sleep(10)
        return response

    def publish_in_telegram_mediagroup(self, token=TELEGRAM_TOKEN, chat_id=CHAT_ID):
        send_media_group = f'https://api.telegram.org/bot{token}/sendMediaGroup'
        files = {}
        media = []
        for i, img in enumerate(self.images):
            with BytesIO() as output:
                with Image.open(PATH + '/' + self.images[i], 'r') as img:
                    img.save(output, format='PNG')
                output.seek(0)
                name = f'photo{i}'
                files[name] = output.read()
                media.append(dict(type='photo', media=f'attach://{name}'))
        media[0]['caption'] = self.caption
        response = requests.post(send_media_group, data={
            'chat_id': chat_id,
            'media': json.dumps(media)},
                                 files=files).json()
        time.sleep(10)
        return response


def download_all_posts():
    L = instaloader.Instaloader(compress_json=False, sanitize_paths=True)
    try:
        L.load_session_from_file(USER, SESSION_FILE)
    except:
        L.login(USER, PASSWORD)  # (login)
    posts = instaloader.Profile.from_username(L.context, PAGE).get_posts()
    for post in posts:
        # print(post.date)
        L.download_post(post, PAGE)
    counter = -1
    return counter


def download_latest_posts():
    # get last date
    files = sorted([f for f in listdir(PATH) if isfile(join(PATH, f))])
    since = [x for x in files if '.json' in x][-1].replace('.json', '')
    since = datetime.strptime(since, '%Y-%m-%d_%H-%M-%S_UTC')
    until = datetime(9999, 4, 20)
    print(since, until)
    # get posts feed
    L = instaloader.Instaloader(compress_json=False, sanitize_paths=True)
    try:
        L.load_session_from_file(USER, SESSION_FILE)
    except:
        L.login(USER, PASSWORD)  # (login)
    posts = instaloader.Profile.from_username(L.context, PAGE).get_posts()
    # download new posts
    k = 0  # initiate k
    counter = 0
    post_dates = []
    for post in posts:
        postdate = post.date
        if postdate > until:
            continue
        elif postdate <= since:
            k += 1
            if k == 50:
                break
            else:
                continue
        else:
            L.download_post(post, PAGE)
            print(post.date_utc)
            post_dates.append(post.date_utc)
            counter += 1
            k = 0  # set k to 0
    return counter


def upload_files(counter):
    # initialize file lists
    files = [f for f in listdir(PATH) if isfile(join(PATH, f))]
    files = sorted(files)
    json_files = [x for x in files if '.json' in x]
    json_files = [w.replace('.json', '') for w in json_files]
    image_files = [x for x in files if '.jpg' in x]
    # check if first run, otherwise cut the list to new posts
    if is_it_first_run():
        json_files = json_files
    else:
        print('setting counter to ' + str(counter))
        if counter > 0:
            json_files = json_files[-int(counter):]
        elif counter == 0:
            json_files = []
        else:
            json_files = json_files
    # grab media, caption for each post
    for filename in json_files:
        images = [x for x in image_files if filename in x]
        if len(images) == 1:
            media_type = 'sendPhoto'
        elif len(images) > 1:
            media_type = 'sendMediaGroup'
        else:
            media_type = 'unknown'
            logging.warning('Cannot publish post ' + filename + ' - format unrecognized.')
        try:
            with open(PATH + '/' + filename + ".txt", "r", encoding="utf-8") as caption:
                caption = caption.readline()[:-1]
        except:
            caption = ''
            pass
        # initialize post object
        output = Post(filename, images, media_type, caption)
        # publish picture, mediagroup or skip video
        if output.media_type == 'sendPhoto':
            response = output.publish_in_telegram()
            logging.info('Publishing picture ' + output.filename + ' - response ' + str(response))
        elif output.media_type == 'sendMediaGroup':
            response = output.publish_in_telegram_mediagroup()
            logging.info('Publishing mediagroup ' + output.filename + ' - response ' + str(response))
        else:
            pass
    return


def is_it_first_run():
    if not exists(PATH) or not any(isfile(join(PATH, i)) for i in listdir(PATH)):
        is_it = True
    else:
        is_it = False
    return is_it


def main():
    if is_it_first_run():
        logging.info('running first run')
        counter = download_all_posts()
        upload_files(counter)
    else:
        logging.info('running update')
        counter = download_latest_posts()
        upload_files(counter)


if __name__ == "__main__":
    # define path variable
    PATH = os.path.dirname(os.path.abspath(__file__))
    SESSION_FILE = os.path.join(PATH, 'session')
    try:
        PATH = os.path.join(PATH, PAGE)
    except:
        logging.warning('Error, configuration file wrong?')
    main()