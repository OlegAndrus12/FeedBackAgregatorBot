import gspread
from google.oauth2.service_account import Credentials

from src.settings import SERVICE_ACCOUNT_FILE, SPREAD_SHEET_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

sheets_client = gspread.authorize(creds)
sheet = sheets_client.open_by_key(SPREAD_SHEET_ID).sheet1
