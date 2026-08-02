import re
import feedparser
import requests
from config import RSS_SOURCES, TARGET_COINS


def clean_html(raw_html: str) -> str:
  """Удаляет HTML-теги и лишние пробелы из текста RSS."""
  clean_text = re.sub(r"<[^>]+>", "", raw_html)
  return " ".join(clean_text.split())


def fetch_top10_news(limit: int = 5) -> list:
  """Сканирует RSS-ленты, парсит заголовок + summary

  и фильтрует новости по монетам из Топ-10.
  """
  filtered_news = []
  seen_titles = set()

  for feed_url in RSS_SOURCES:
    try:
      feed = feedparser.parse(feed_url)

      for entry in feed.entries:
        title = getattr(entry, "title", "")
        title_upper = title.upper()

        if not title or title_upper in seen_titles:
          continue

        raw_summary = getattr(entry, "summary", "")
        summary_text = clean_html(raw_summary) if raw_summary else title
        search_target = f"{title_upper} {summary_text.upper()}"

        found_coin = None
        for coin_code, keywords in TARGET_COINS.items():
          if any(kw in search_target for kw in keywords):
            found_coin = coin_code
            break

        if found_coin:
          seen_titles.add(title_upper)
          filtered_news.append({
              "title": title,
              "summary": summary_text,
              "url": getattr(entry, "link", ""),
              "coin": f"{found_coin}USDT",
              "raw_coin": found_coin,
          })

        if len(filtered_news) >= limit:
          return filtered_news

    except Exception as e:
      print(f"Ошибка парсинга RSS {feed_url}: {e}")

  return filtered_news


def get_advanced_coin_metrics(symbol: str = "BTCUSDT") -> dict:
  """Запрашивает котировки, фандинг, OI, объем 24h и L/S ratio с Bybit V5."""
  symbol = symbol.upper()
  if not symbol.endswith("USDT"):
    symbol = f"{symbol}USDT"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    ticker_url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
    res = requests.get(ticker_url, headers=headers, timeout=5).json()

    if res.get("retCode") != 0 or not res.get("result", {}).get("list"):
      print(f"Монета {symbol} не найдена на Bybit Futures.")
      return None

    data = res["result"]["list"][0]

    price = float(data.get("lastPrice", 0))
    price_change_24h = float(data.get("price24hPcnt", 0)) * 100
    funding_rate = float(data.get("fundingRate", 0)) * 100
    open_interest_coins = float(data.get("openInterest", 0))
    volume_24h_usd = float(data.get("turnover24h", 0))

    open_interest_usd = open_interest_coins * price

    ls_url = f"https://api.bybit.com/v5/market/account-ratio?category=linear&symbol={symbol}&period=1d&limit=1"
    ls_res = requests.get(ls_url, headers=headers, timeout=5).json()

    buy_ratio, sell_ratio = 50.0, 50.0
    if ls_res.get("retCode") == 0 and ls_res.get("result", {}).get("list"):
      ls_data = ls_res["result"]["list"][0]
      buy_ratio = round(float(ls_data.get("buyRatio", 0.5)) * 100, 1)
      sell_ratio = round(float(ls_data.get("sellRatio", 0.5)) * 100, 1)

    return {
        "symbol": symbol,
        "price_usd": round(price, 2) if price >= 1 else round(price, 4),
        "change_24h_pct": round(price_change_24h, 2),
        "funding_rate_pct": round(funding_rate, 4),
        "open_interest_m_usd": round(open_interest_usd / 1_000_000, 2),
        "volume_24h_m_usd": round(volume_24h_usd / 1_000_000, 2),
        "long_short_ratio": f"{buy_ratio}% Лонги / {sell_ratio}% Шорты",
    }

  except Exception as e:
    print(f"Ошибка получения метрик Bybit по {symbol}: {e}")
    return None