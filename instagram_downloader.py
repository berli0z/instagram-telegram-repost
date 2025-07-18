"""Instagram downloader module."""
import logging
import os
from datetime import datetime
from os import listdir
from os.path import isfile, join, exists
import instaloader


class InstagramDownloader:
    """Handle Instagram post downloading."""
    
    def __init__(self, username, password, page, base_path):
        self.username = username
        self.password = password
        self.page = page
        self.base_path = base_path
        self.page_path = os.path.join(base_path, page)
        self.session_file = os.path.join(base_path, 'session')
        self.loader = instaloader.Instaloader(compress_json=False, sanitize_paths=True)
        
    def _ensure_login(self):
        """Ensure we're logged in to Instagram."""
        try:
            self.loader.load_session_from_file(self.username, self.session_file)
            logging.info('Loaded existing session')
        except Exception as e:
            logging.info(f'Session load failed: {e}, logging in...')
            try:
                self.loader.login(self.username, self.password)
                logging.info('Successfully logged in')
            except Exception as login_error:
                logging.error(f'Login failed: {login_error}')
                raise
                
    def is_first_run(self):
        """Check if this is the first run for this page."""
        if not exists(self.page_path):
            return True
        
        files = [f for f in listdir(self.page_path) if isfile(join(self.page_path, f))]
        json_files = [x for x in files if '.json' in x]
        
        return len(json_files) == 0
        
    def download_all_posts(self):
        """Download all posts from the Instagram page."""
        self._ensure_login()
        
        try:
            profile = instaloader.Profile.from_username(self.loader.context, self.page)
            posts = profile.get_posts()
            
            count = 0
            for post in posts:
                try:
                    self.loader.download_post(post, self.page)
                    count += 1
                    logging.info(f'Downloaded post from {post.date}')
                except Exception as e:
                    logging.warning(f'Failed to download post from {post.date}: {e}')
                    
            logging.info(f'Downloaded {count} posts in total')
            return -1  # Indicates all posts downloaded
            
        except Exception as e:
            logging.error(f'Failed to download posts: {e}')
            raise
            
    def download_latest_posts(self):
        """Download only new posts since last run."""
        if self.is_first_run():
            logging.info('No previous posts found, downloading all posts')
            return self.download_all_posts()
            
        self._ensure_login()
        
        try:
            # Get last post date
            files = sorted([f for f in listdir(self.page_path) if isfile(join(self.page_path, f))])
            json_files = [x for x in files if '.json' in x]
            
            if not json_files:
                logging.warning('No JSON files found despite not being first run')
                return self.download_all_posts()
                
            since_filename = json_files[-1].replace('.json', '')
            since = datetime.strptime(since_filename, '%Y-%m-%d_%H-%M-%S_UTC')
            until = datetime(9999, 4, 20)
            
            logging.info(f'Downloading posts since {since}')
            
            profile = instaloader.Profile.from_username(self.loader.context, self.page)
            posts = profile.get_posts()
            
            counter = 0
            consecutive_old_posts = 0
            post_dates = []
            
            for post in posts:
                postdate = post.date
                
                if postdate > until:
                    continue
                elif postdate <= since:
                    consecutive_old_posts += 1
                    if consecutive_old_posts >= 50:
                        logging.info('Found 50 consecutive old posts, stopping')
                        break
                    continue
                else:
                    try:
                        self.loader.download_post(post, self.page)
                        logging.info(f'Downloaded new post from {post.date_utc}')
                        post_dates.append(post.date_utc)
                        counter += 1
                        consecutive_old_posts = 0
                    except Exception as e:
                        logging.warning(f'Failed to download post from {post.date}: {e}')
                        
            logging.info(f'Downloaded {counter} new posts')
            return counter
            
        except Exception as e:
            logging.error(f'Failed to download latest posts: {e}')
            raise