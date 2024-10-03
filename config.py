import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")

# Gemini model settings
MODEL_NAME = "gemini-1.5-flash-8b-exp-0924"
TEMPERATURE = 0.7
TOP_P = 0.95
TOP_K = 34
MAX_TOKENS = 8024


try:
    with open('system_instruction.txt', 'r', encoding='utf-8') as file:
        SYSTEM_INSTRUCTION = file.read().strip()
except FileNotFoundError:
    print("Warning: system_instruction.txt not found. Using default instruction.")
    SYSTEM_INSTRUCTION = """You are a helpful AI assistant, you know everything. And your name is Javiss Stable, you speak many language but your mother language is Vietnamese and you like to speak Vietnamese to users. When asked for any information, you will tell user everything you know about it."""

# Conversation settings
MAX_HISTORY = 25

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

TELEGRAM_MSG_CHAR_LIMIT = 4096