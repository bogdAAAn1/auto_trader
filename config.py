import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "1h")
QUANTITY = float(os.getenv("QUANTITY", "0.001"))
TESTNET = os.getenv("TESTNET", "True") == "True"
BASE_URL = os.getenv("BASE_URL", "https://testnet.binance.vision/api")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PORT = os.getenv("PORT")
