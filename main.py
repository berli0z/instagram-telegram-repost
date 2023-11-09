from datetime import datetime
import instaloader
from config import *
from os import listdir
import requests
import time
from io import BytesIO
import json
from PIL import Image
from os.path import isfile, join, exists
import os
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG, filename='itr.log')
logging.info('So should this')
logging.warning('And this, too')

# working directory path fix if run from crontab
logging.debug('Current working dir: '+os.getcwd())
if 'instagram-telegram-repost' not in os.getcwd():
    logging.warning('Changing working directory to: '+os.getcwd() + '/instagram-telegram-repost')
    os.chdir(os.getcwd() + '/instagram-telegram-repost')
    print(os.getcwd())
    logging.warning('Working dir changed to: '+os.getcwd())
PATH = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(PATH, 'session')
PATH = os.path.join(PATH, PAGE)

# TO DO
# Add compatibility with videos?
# Add cli interface?
# Add telegram interface?
# Add logging
# https://instaloader.github.io/troubleshooting.html#login-error
# Add readme file with instructions
# create github repo

# Handle the case in which you are unlogged? (get new session?)


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
        SEND_MEDIA_GROUP = f'https://api.telegram.org/bot{token}/sendMediaGroup'
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
        return requests.post(SEND_MEDIA_GROUP, data={'chat_id': chat_id, 'media': json.dumps(media)}, files=files)


def download_all_posts():
    L = instaloader.Instaloader(compress_json=False, sanitize_paths=True)
    '''  try:
        L.login(USER, PASSWORD)  # (login)
    except:'''
    L.load_session_from_file(USER, SESSION_FILE)
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
        L.login(USER, PASSWORD)  # (login)
    except:
        L.load_session_from_file(USER, SESSION_FILE)
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

    for filename in json_files:
        images = [x for x in image_files if filename in x]
        if len(images) == 1:
            media_type = 'sendPhoto'
        else:
            media_type = 'sendMediaGroup'
        try:
            with open(PATH + '/' + filename + ".txt", "r", encoding="utf-8") as caption:
                caption = caption.readline()[:-1]
        except:
            caption = ''
            pass
        output = Post(filename, images, media_type, caption)
        # print(vars(output))
        if output.media_type == 'sendPhoto':
            response = output.publish_in_telegram()
            # print(response)
        elif output.media_type == 'sendMediaGroup':
            response = output.publish_in_telegram_mediagroup()
            # print(response)
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


if __name__ == '__main__':
    main()
