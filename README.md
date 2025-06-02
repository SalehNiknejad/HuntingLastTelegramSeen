# HuntingLastTelegramSeen

A Python Telegram bot that monitors the online status (Last Seen) of specific users and sends updates to a group or channel when their status changes.

## 🚀 Features

- Monitor multiple Telegram users
- Detects changes in online/offline status
- Sends updates to a target group/channel (optionally silent per user)
- Assign aliases to users for readability
- Keeps logs of status changes
- Environment variables and user list are stored safely via `.env` and `users.json`

## 📦 Requirements

- Python 3.8+
- A Telegram API ID and Hash from [my.telegram.org](https://my.telegram.org)
- A group/channel where the bot can post updates

## 🔧 Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/SalehNiknejad/HuntingLastTelegramSeen.git
   cd HuntingLastTelegramSeen
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:

   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   TARGET_CHAT_ID=@yourchannelorchatid
   ```

4. Create your `users.json` based on the `users.example.json`.

5. Run the bot:
   ```bash
   python hunter.py
   ```

## 🛡 Security

Your `.env` file is ignored by Git and should **never** be committed. The `.env.example` file is a safe template for others.

## 📄 License

MIT
