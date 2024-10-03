# Gemini Telegram Bot

This is a Telegram bot powered by Google's Gemini AI, capable of handling both text and images.  The entire project's source code is written in Python, by Claude 3.5 Sonnet based on Huân's requirements and workflow, then refined and enhanced with additional features.

## Features:

- Text message processing
- Image analysis (with or without captions)
- PDF file handling
- Access restrictions for specific users
- Storage and use of conversation history
- HTML formatted responses

## Requirements:

- Python 3.9+ (I am using Python 3.11 on Ubuntu 20.04).
- A Telegram Bot Token (obtained by creating a new bot using BotFather).
- A Google API Key for Gemini.

## Installation

1. Clone this repository:
```
git clone https://github.com/kevinkieu/gemini-stable.git
```
Navigate to the project root directory:
```
cd gemini-stable
```
2. Install required libraries:
```
pip install python-telegram-bot google-generativeai python-dotenv Pillow pdfplumber
```

3. Create a `.env` file in the project root directory and add the following information:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_API_KEY=your_google_api_key_here
ALLOWED_USERS=username1,username2,username3
```
Note: The bot will not function without these environment variables.

4. Create a `system_instruction.txt` file in the project root and add the system instructions for the bot:  (e.g., You are a helpful AI assistant...)


## Project Structure

- `main.py`: The main file to run the bot
- `telegram_handler.py`: Handles Telegram interactions
- `gemini_handler.py`: Handles interactions with the Gemini API
- `config.py`: Configuration and environment variables
- `conversation_manager.py`: Manages conversation history
- `utils.py`: Utility functions
- `html_format.py`: Formats messages in HTML
- `system_instruction.txt`: System instructions for the bot


## Usage

1. Run the bot:
```
python main.py
```
   or
```
python3 main.py
```

2. In Telegram, start a conversation with your bot.

3. Send text messages or images to receive responses from the bot.


## Commands

- /start: Starts a conversation with the bot
- /clear: Clears the conversation history


## Customization

- To change the system instructions, edit the `system_instruction.txt` file.
- To add or remove allowed users, update the ALLOWED_USERS variable in the `.env` file.


## Contributing

All contributions are welcome.  Please open an issue or create a pull request to contribute. You can also ping me on Telegram at @huank8895.
