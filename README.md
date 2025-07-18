# Instagram Telegram Repost

A robust, modular Python application to backup Instagram pages as Telegram channels and keep them updated automatically.

## Key Features

- **Reliable**: Improved error handling and crash prevention
- **Modular**: Clean separation of concerns with dedicated modules for configuration, Instagram downloading, and Telegram uploading
- **Long-running**: Better session management and rate limiting for sustained operation
- **Configurable**: Flexible configuration via command line arguments or config files

## How it works

The application downloads Instagram posts (excluding videos) from a specified page and uploads them to your Telegram channel. On first run, it downloads all posts. Subsequent runs only download and upload new posts, making it efficient for regular updates.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/berli0z/instagram-telegram-repost.git
   cd instagram-telegram-repost
   ```

2. Install requirements:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Configure the application (see [Configuration](#configuration))

4. Run the application:
   ```bash
   python3 main.py -c config.conf
   ```

## Configuration

### Method 1: Configuration File

1. Copy the sample configuration file:
   ```bash
   cp sample_config.conf config.conf
   ```

2. Edit `config.conf` with your details:
   ```ini
   [Defaults]
   page = INSTAGRAM_PAGE_HANDLE
   username = YOUR_INSTAGRAM_USERNAME
   password = YOUR_INSTAGRAM_PASSWORD
   chat-id = TELEGRAM_CHAT_ID
   bot-token = TELEGRAM_BOT_TOKEN
   ```

### Method 2: Command Line Arguments

```bash
python3 main.py -p instagram_page -u username -k password -i chat_id -t bot_token
```

### Getting Required Information

- **Bot Token**: Follow [this guide](https://archive.is/p7SsD) to create a Telegram bot
- **Chat ID**: Use [@username_to_id_bot](https://t.me/username_to_id_bot) to get your channel's chat ID

## Command Line Options

```
-c, --config_file    Configuration file (default: config.conf)
-p, --page          Instagram page handle
-u, --username      Your Instagram username
-k, --password      Your Instagram password  
-i, --chat-id       Telegram chat ID
-t, --bot-token     Telegram bot token
```

## Architecture

The application is built with a modular architecture:

- **`config_handler.py`**: Handles configuration loading and validation
- **`instagram_downloader.py`**: Manages Instagram authentication and post downloading
- **`telegram_uploader.py`**: Handles Telegram API interactions and media uploads
- **`main.py`**: Main application orchestrator

This modular design makes the application:
- Easier to maintain and extend
- More testable
- Better at handling errors
- Simpler to debug

## Troubleshooting

### Login Issues

If you experience login issues or get logged out frequently (common with VPS hosting), use the `get_cookie.py` utility:

```bash
python3 get_cookie.py
```

This extracts Instagram cookies from your local Firefox browser for use on remote servers.

### Common Issues

- **First run crashes**: Fixed in this version with proper error handling
- **Rate limiting**: The application includes built-in delays to respect API limits
- **Session management**: Improved session handling for better reliability

## Running Automatically

For automated operation, add to your crontab:

```bash
# Run every hour
0 * * * * cd /path/to/instagram-telegram-repost && python3 main.py -c config.conf
```

The application handles working directory changes automatically for crontab compatibility.

## Logging

The application creates detailed logs in `logs.log` for troubleshooting and monitoring. Logs include both file output and console output for better visibility.

## Quick Start

```bash
python3 main.py -p page -u username -k password -i chat_id -t bot_token
```