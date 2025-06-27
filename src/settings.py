import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SRC_FOLDER = BASE_DIR / "src"

SERVICE_ACCOUNT_FILE = BASE_DIR / "credentials.json"
SPREAD_SHEET_ID = os.getenv("SPREAD_SHEET_ID")
TOTAL_QUESTIONS = 8
BOT_TOKEN = os.getenv("BOT_TOKEN")
