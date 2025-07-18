"""
Instagram Telegram Repost - Modular Version
A refactored and improved version of the Instagram-Telegram repost tool.
"""
import logging
import os
import sys

from config_handler import ConfigHandler
from instagram_downloader import InstagramDownloader
from telegram_uploader import TelegramUploader


class InstagramTelegramRepost:
    """Main application class for Instagram-Telegram reposting."""
    
    def __init__(self):
        self.config = ConfigHandler()
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.instagram_downloader = None
        self.telegram_uploader = None
        
    def setup_logging(self):
        """Configure logging."""
        log_format = '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s'
        
        # Create logs directory if it doesn't exist
        log_file = os.path.join(self.base_path, 'logs.log')
        
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def load_configuration(self, args=None):
        """Load and validate configuration."""
        try:
            self.config.load_from_args(args)
            self.config.validate()
            logging.info(f'Configuration loaded successfully for page: {self.config.page}')
            return True
        except Exception as e:
            logging.error(f'Configuration error: {e}')
            return False
            
    def initialize_components(self):
        """Initialize Instagram downloader and Telegram uploader."""
        try:
            # Fix working directory if needed (for crontab compatibility)
            if 'instagram-telegram-repost' not in os.getcwd():
                new_path = os.path.join(os.getcwd(), 'instagram-telegram-repost')
                if os.path.exists(new_path):
                    os.chdir(new_path)
                    self.base_path = os.getcwd()
                    logging.info(f'Changed working directory to: {self.base_path}')
                    
            self.instagram_downloader = InstagramDownloader(
                username=self.config.username,
                password=self.config.password,
                page=self.config.page,
                base_path=self.base_path
            )
            
            self.telegram_uploader = TelegramUploader(
                bot_token=self.config.bot_token,
                chat_id=self.config.chat_id,
                base_path=os.path.join(self.base_path, self.config.page)
            )
            
            logging.info('Components initialized successfully')
            return True
            
        except Exception as e:
            logging.error(f'Failed to initialize components: {e}')
            return False
            
    def run(self, args=None):
        """Main execution method."""
        self.setup_logging()
        
        logging.info('Starting Instagram-Telegram Repost')
        
        # Load configuration
        if not self.load_configuration(args):
            logging.error('Failed to load configuration. Please check your config file or arguments.')
            return False
            
        # Initialize components
        if not self.initialize_components():
            logging.error('Failed to initialize components.')
            return False
            
        try:
            # Check if first run
            is_first_run = self.instagram_downloader.is_first_run()
            
            if is_first_run:
                logging.info('First run detected - downloading all posts')
                counter = self.instagram_downloader.download_all_posts()
            else:
                logging.info('Updating - downloading new posts only')
                counter = self.instagram_downloader.download_latest_posts()
                
            # Upload to Telegram
            logging.info('Starting Telegram upload')
            page_path = os.path.join(self.base_path, self.config.page)
            uploaded_count = self.telegram_uploader.upload_files(page_path, counter, is_first_run)
            
            logging.info(f'Process completed successfully. Uploaded {uploaded_count} posts.')
            return True
            
        except Exception as e:
            logging.error(f'Process failed: {e}')
            return False


def main():
    """Entry point for the application."""
    app = InstagramTelegramRepost()
    success = app.run()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()