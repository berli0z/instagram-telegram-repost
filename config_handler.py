"""Configuration handler for Instagram-Telegram Repost."""
import configparser
import logging
import os
from argparse import ArgumentParser


class ConfigHandler:
    """Handle configuration loading and validation."""
    
    def __init__(self):
        self.page = None
        self.username = None
        self.password = None
        self.chat_id = None
        self.bot_token = None
        self.config_file = None
        
    def load_from_args(self, args=None):
        """Load configuration from command line arguments and config file."""
        parser = ArgumentParser()
        parser.add_argument("-c", "--config_file", default='config.conf', type=str, help='Config file')
        parser.add_argument("-p", "--page", help="Instagram page handle")
        parser.add_argument("-u", "--username", help="Instagram username")
        parser.add_argument("-k", "--password", help="Instagram password")
        parser.add_argument("-i", "--chat-id", help="Telegram chat ID")
        parser.add_argument("-t", "--bot-token", help="Telegram bot token")
        
        parsed_args = parser.parse_args(args)
        
        # Load from config file if specified
        if parsed_args.config_file and os.path.exists(parsed_args.config_file):
            self._load_from_config_file(parsed_args.config_file)
            
        # Override with command line arguments
        if parsed_args.page:
            self.page = parsed_args.page
        if parsed_args.username:
            self.username = parsed_args.username
        if parsed_args.password:
            self.password = parsed_args.password
        if parsed_args.chat_id:
            self.chat_id = parsed_args.chat_id
        if parsed_args.bot_token:
            self.bot_token = parsed_args.bot_token
            
        self.config_file = parsed_args.config_file
        
    def _load_from_config_file(self, config_file):
        """Load configuration from config file."""
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if 'Defaults' in config:
                defaults = config['Defaults']
                self.page = defaults.get('page', self.page)
                self.username = defaults.get('username', self.username)
                self.password = defaults.get('password', self.password)
                self.chat_id = defaults.get('chat-id', self.chat_id)
                self.bot_token = defaults.get('bot-token', self.bot_token)
                
        except Exception as e:
            logging.warning(f'Error reading config file {config_file}: {e}')
            
    def validate(self):
        """Validate that all required configuration is present."""
        missing = []
        
        if not self.page:
            missing.append('page')
        if not self.username:
            missing.append('username')
        if not self.password:
            missing.append('password')
        if not self.chat_id:
            missing.append('chat_id')
        if not self.bot_token:
            missing.append('bot_token')
            
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
            
        return True
        
    def __repr__(self):
        """String representation (hiding sensitive info)."""
        return (f"ConfigHandler(page='{self.page}', username='{self.username}', "
                f"chat_id='{self.chat_id}', bot_token='***', password='***')")