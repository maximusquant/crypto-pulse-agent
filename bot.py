import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


def send_to_telegram(text: str) -> bool:
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
    print("Токены Telegram не найдены в .env.")
    return False

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHANNEL_ID,
      "text": text,
      "disable_web_page_preview": False,  # ВКЛЮЧАЕТ авто-картинку и превью ссылки!
      "parse_mode": "Markdown",
  }

  try:
    res = requests.post(url, json=payload, timeout=10)
    res_data = res.json()

    if res.status_code == 200 and res_data.get("ok"):
      print("ПОСТ С ПРЕВЬЮ УСПЕШНО ОПУБЛИКОВАН!")
      return True
    else:
      print(f"Ошибка Telegram API: {res_data}")
      return False
  except Exception as e:
    print(f"Ошибка соединения: {e}")
    return False