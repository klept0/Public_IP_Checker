# Public IP Checker

This Python script monitors your public IP address and sends notifications via [Apprise](https://github.com/caronc/apprise) when your IP changes. It supports verbose testing and can be configured for multiple notification services (Telegram, Pushover, etc).

## Features

- Notifies you via Apprise when your public IP changes
- Stores previous IP locally to detect changes
- Verbose mode for testing: prints IP every 90 seconds for 5 minutes, then sends a test notification
- Easy configuration via JSON file

## Requirements

- Python 3.7+
- [Apprise](https://github.com/caronc/apprise) (`pip install apprise`)
- `requests` library (`pip install requests`)

## Setup

1. **Clone this repo or copy the files.**
2. **Install dependencies:**
   ```sh
   pip install requests apprise
   ```
3. **Create `apprise_config.json` in the same directory:**
   ```json
   {
     "apprise_urls": [
       "pover://YOUR_PUSHOVER_USER@YOUR_PUSHOVER_TOKEN/",
       "tgram://YOUR_BOT_TOKEN/YOUR_CHAT_ID"
     ]
   }
   ```
   Replace with your actual Apprise URLs.

4. **Run the script:**
   ```sh
   python main.py
   ```
   For verbose testing mode:
   ```sh
   python main.py --verbose
   ```

## Files

- `main.py` — Main script
- `apprise_config.json` — Notification configuration
- `PreviousIP.txt` — Stores the last known public IP
- `heartbeat.json` — (Optional) Tracks uptime and IP change stats

## Security

- All file paths are constructed safely and do not use user input.
- Do not share your `apprise_config.json` with others as it contains your notification credentials.

## License

MIT License
