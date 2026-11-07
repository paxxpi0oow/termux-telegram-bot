# Ultimate Termux Telegram Bot

Control your Android phone remotely via Telegram using Termux:API. 

## Features
- 🔋 `/battery` - Check battery status with visual bar
- 📸 `/photo` & `/selfie` - Take photos remotely
- 📍 `/location` - Get GPS coordinates and Google Maps link
- 🔦 `/torch` & `/vibrate` - Flashlight and vibration control
- 💻 `/sh [command]` - Run Linux terminal commands remotely
- 📁 `/download [path]` - Download files from phone to Telegram

## Requirements
- Termux (F-Droid)
- Termux:API app
- `pkg install python termux-api`
- `pip install requests`

## Setup
1. Create a bot on Telegram via `@BotFather` and get the Token.
2. Get your Chat ID via `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Edit `bot.py` and insert your TOKEN and CHAT_ID.
4. Run `python bot.py`
