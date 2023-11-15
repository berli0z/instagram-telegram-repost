# Instagram Telegram Repost
A python script to backup an instagram page as a telegram channel and keep it updated.

## How it works
After setting up the configuration, the first time you run the script on a single page it will download all its posts (expect videos) and then upload them to you channel. When you run it again on the same page, it will update the posts and only upload those. You will need an instagram account, a telegram channel and a telegram bot of your own (see below for more details). You can run the process in crontab, but you will get logged out often if your VPS is hosted and/or your account is relatively new.

## Installation
0. git clone this repository: `git clone https://github.com/berli0z/instagram-telegram-repost.git`
1. Install requirements.txt `python3 -m pip install -r requirements.txt`
2. Edit the configuration file and rename it (see [Configuration](#configuration)) `nano sample_config.conf`, and saves as `config.conf`
3. Run with `python3 main.py -c config.conf` or use arguments (see [Arguments](#arguments))

## Configuration
- Edit the variables in sample_config.conf and save as config.conf in instagram-telegram-repost folder.
- In order to get a **bot token**, please follow this [guide](https://archive.is/p7SsD). 
- To get a **chat id**, you can use this [telegram bot](https://t.me/username_to_id_bot) instead.
```
[Defaults]
page = INSTAGRAM_PAGE_HANDLE_YOU_WANT_TO_FORWARD
username = YOUR_INSTAGRAM_ACCOUNT_USERNAME
password = YOUR_INSTAGRAM_ACCOUNT_PASSWORD
chat_id = TELEGRAM_CHAT_ID_OF_FORWARDING_CHANNEL/GROUP
bot_token = TELGRAM_BOT_TOKEN
```

## Arguments
Example usage: `python3 main.py -p instagram -u user -k 1234 -i -100123435345 -t bottoken:1512413525151521`

```
-p; --page: the name of the instagram handle to forward
-u; --username: your own instagram username
-k; --password: your instagram account password
-i; --chat-id: the chat-id of the telegram channel/group you want to forward to
-t; --token: the telegram bot token
-c; --config: a configuration file based on sample_config.conf
```
## Troubleshooting
If you are logged out or cannot run the script from a VPS, consider using `get
_cookie.py` to get a cookie either locally or to get it from your local computer and use it on the VPS.

## FAQ
- I have a problem, how do I solve it?
- Please, open an issue with your details and I will try to fix it. Thank you.

## TL;DR
`python3 main.py -p page -u username -k password -i chat_id -t bot_token`
