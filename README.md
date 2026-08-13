# Telegram Video Editor Bot

This is a Telegram bot that automatically edits videos to make them copyright-safe.

## Features
- **Crop**: Slight video cropping.
- **Mirror**: Horizontal flip.
- **Color Correction**: Adjusts brightness, contrast, and saturation.
- **Watermark**: Adds a text watermark ("Digital Skill BD").
- **Audio Modulation**: Modifies pitch and tempo.

## Requirements
- Python 3.x
- `pyTelegramBotAPI`
- `ffmpeg` (must be installed on the system)

## Setup
1. Clone this repository.
2. Install requirements: `pip install -r requirements.txt`.
3. Set your token in `bot.py`.
4. Run the bot: `python bot.py`.
