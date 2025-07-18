"""Telegram uploader module."""
import json
import logging
import time
from io import BytesIO
from os import listdir
from os.path import isfile, join

import requests
from PIL import Image


class Post:
    """Represents a single Instagram post to be uploaded to Telegram."""
    
    def __init__(self, filename, images, media_type, caption):
        self.filename = filename
        self.images = images
        self.media_type = media_type
        self.caption = caption
        
    def __repr__(self):
        return f"Post(filename='{self.filename}', media_type='{self.media_type}', images_count={len(self.images)})"


class TelegramUploader:
    """Handle uploading posts to Telegram."""
    
    def __init__(self, bot_token, chat_id, base_path):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_path = base_path
        
    def _send_single_photo(self, post):
        """Send a single photo to Telegram."""
        try:
            image_path = join(self.base_path, post.images[0])
            
            with open(image_path, 'rb') as photo:
                response = requests.post(
                    url=f'https://api.telegram.org/bot{self.bot_token}/sendPhoto',
                    data={'chat_id': self.chat_id, 'caption': post.caption},
                    files={'photo': photo}
                )
                
            response.raise_for_status()
            time.sleep(10)  # Rate limiting
            return response.json()
            
        except Exception as e:
            logging.error(f'Failed to send single photo {post.filename}: {e}')
            raise
            
    def _send_media_group(self, post):
        """Send multiple photos as a media group to Telegram."""
        try:
            send_media_group_url = f'https://api.telegram.org/bot{self.bot_token}/sendMediaGroup'
            files = {}
            media = []
            
            for i, img_filename in enumerate(post.images):
                image_path = join(self.base_path, img_filename)
                
                with BytesIO() as output:
                    with Image.open(image_path, 'r') as img:
                        img.save(output, format='PNG')
                    output.seek(0)
                    name = f'photo{i}'
                    files[name] = output.read()
                    media.append({'type': 'photo', 'media': f'attach://{name}'})
                    
            # Add caption to first image
            if media:
                media[0]['caption'] = post.caption
                
            response = requests.post(
                send_media_group_url,
                data={
                    'chat_id': self.chat_id,
                    'media': json.dumps(media)
                },
                files=files
            )
            
            response.raise_for_status()
            time.sleep(10)  # Rate limiting
            return response.json()
            
        except Exception as e:
            logging.error(f'Failed to send media group {post.filename}: {e}')
            raise
            
    def upload_post(self, post):
        """Upload a single post to Telegram."""
        if post.media_type == 'sendPhoto':
            return self._send_single_photo(post)
        elif post.media_type == 'sendMediaGroup':
            return self._send_media_group(post)
        else:
            logging.warning(f'Unknown media type for post {post.filename}: {post.media_type}')
            return None
            
    def upload_files(self, page_path, counter, is_first_run):
        """Upload files to Telegram based on counter."""
        try:
            # Get all files
            files = [f for f in listdir(page_path) if isfile(join(page_path, f))]
            files = sorted(files)
            
            json_files = [x for x in files if '.json' in x]
            json_files = [w.replace('.json', '') for w in json_files]
            image_files = [x for x in files if '.jpg' in x]
            
            # Determine which posts to upload
            if is_first_run:
                posts_to_upload = json_files
                logging.info(f'First run: uploading all {len(posts_to_upload)} posts')
            else:
                if counter > 0:
                    posts_to_upload = json_files[-int(counter):]
                    logging.info(f'Uploading {len(posts_to_upload)} new posts')
                elif counter == 0:
                    posts_to_upload = []
                    logging.info('No new posts to upload')
                else:
                    posts_to_upload = json_files
                    logging.info(f'Uploading all {len(posts_to_upload)} posts')
                    
            uploaded_count = 0
            
            # Process each post
            for filename in posts_to_upload:
                try:
                    post = self._create_post_from_files(filename, image_files, page_path)
                    if post:
                        response = self.upload_post(post)
                        if response:
                            uploaded_count += 1
                            logging.info(f'Successfully uploaded {post.media_type}: {post.filename}')
                        else:
                            logging.warning(f'Failed to upload post: {post.filename}')
                    else:
                        logging.warning(f'Could not create post from files: {filename}')
                        
                except Exception as e:
                    logging.error(f'Error processing post {filename}: {e}')
                    
            logging.info(f'Upload complete: {uploaded_count}/{len(posts_to_upload)} posts uploaded')
            return uploaded_count
            
        except Exception as e:
            logging.error(f'Failed to upload files: {e}')
            raise
            
    def _create_post_from_files(self, filename, image_files, page_path):
        """Create a Post object from files."""
        try:
            # Find images for this post
            images = [x for x in image_files if filename in x]
            
            if len(images) == 1:
                media_type = 'sendPhoto'
            elif len(images) > 1:
                media_type = 'sendMediaGroup'
            else:
                logging.warning(f'No images found for post {filename}')
                return None
                
            # Read caption
            caption = ''
            caption_file = join(page_path, filename + '.txt')
            try:
                with open(caption_file, 'r', encoding='utf-8') as f:
                    caption = f.readline().rstrip()
            except FileNotFoundError:
                logging.info(f'No caption file found for {filename}')
            except Exception as e:
                logging.warning(f'Error reading caption for {filename}: {e}')
                
            return Post(filename, images, media_type, caption)
            
        except Exception as e:
            logging.error(f'Error creating post from files {filename}: {e}')
            return None