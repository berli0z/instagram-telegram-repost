# Instagram Telegram Repost
A python script to backup an instagram page and keep it updated.

## Installation
1. Install requirements
2. Edit the configuration file and rename it (see Configuration)
3. Run with python3 main.py -c config.conf or use arguments (see Arguments)

## Configuration
- Edit the CAPS LOCK variables and save to config.conf in instagram-telegram-repost folder.
- In order to get a bot token, please follow this [guide](https://archive.is/p7SsD). 
- To get a chat id, you can use this [telegram bot](https://t.me/username_to_id_bot) instead.
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
- I have a problem, how do i solve it?
- Please, open an issue with your details and i will try to fix it. Thank you.

## TL;DR
`python3 main.py -p page -u username -k password -i chat_id -t bot_token`
