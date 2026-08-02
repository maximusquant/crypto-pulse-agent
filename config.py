import os
from dotenv import load_dotenv

load_dotenv()

# Ключи и токены из .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Фильтры: Фокус исключительно на Top-10 крипто-активах
TARGET_COINS = {
    "BTC": ["BTC", "BITCOIN"],
    "ETH": ["ETH", "ETHEREUM"],
    "SOL": ["SOL", "SOLANA"],
    "BNB": ["BNB", "BINANCE"],
    "XRP": ["XRP", "RIPPLE"],
    "ADA": ["ADA", "CARDANO"],
    "AVAX": ["AVAX", "AVALANCHE"],
    "DOGE": ["DOGE", "DOGECOIN"],
    "DOT": ["DOT", "POLKADOT"],
    "LINK": ["LINK", "CHAINLINK"],
}

# Валидные крипто-источники
RSS_SOURCES = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cryptopotato.com/feed/",
    "https://decrypt.co/feed",
]