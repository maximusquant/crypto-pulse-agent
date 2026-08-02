import requests
from config import GEMINI_API_KEY

# Каскадный список моделей
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]


def generate_post_final(news_item: dict, market_metrics: dict = None) -> str:
  """Генерирует аналитический пост для Telegram на основе новости и метрик Bybit,

  используя прямой REST-запрос к Gemini API с fallback по моделям.
  """
  title = news_item.get("title", "")
  summary = news_item.get("summary", "")
  link = news_item.get("url") or news_item.get("link", "")
  coin = news_item.get("coin", "BTCUSDT")

  # Форматируем блок метрик Bybit
  metrics_text = "Данные по рынку недоступны."
  if market_metrics:
    metrics_text = (
        f"Тикер: {market_metrics.get('symbol', coin)}\n"
        f"Цена: ${market_metrics.get('price_usd', 'N/A')} "
        f"({market_metrics.get('change_24h_pct', 0)}% за 24ч)\n"
        f"Объем 24ч: ${market_metrics.get('volume_24h_m_usd', 'N/A')}M\n"
        f"Открытый интерес (OI):"
        f" ${market_metrics.get('open_interest_m_usd', 'N/A')}M\n"
        f"Фандинг: {market_metrics.get('funding_rate_pct', 'N/A')}%\n"
        f"Сентимент: {market_metrics.get('long_short_ratio', 'N/A')}"
    )

  prompt = f"""
Ты — профессиональный финансовый аналитик и эксперт по криптовалютным рынкам. 
Проанализируй новость вместе с биржевыми данными Bybit и напиши структурированный пост для Telegram.

НОВОСТЬ:
Заголовок: {title}
Контекст: {summary}

БИРЖЕВЫЕ МЕТРИКИ (BYBIT FUTURES):
{metrics_text}

Сформируй ответ СТРОГО по следующей структуре (сохраняй эмодзи и заголовки):

📈 [Короткий цепляющий заголовок/клиповый вывод]

📌 СУТЬ
[1-2 предложения, раскрывающие суть события]

📊 МЕТРИКИ РЫНКА
[Опиши ключевые цифры: динамику цены, сентимент (лонги/шорты), OI или фандинг]

🎯 ВЛИЯНИЕ И ИНСАЙТ
[Свяжи новостной инфоповод с метриками Bybit. Объясни, что происходит на самом деле]

🔮 ПРОГНОЗ
[Краткосрочный сценарий или ключевые триггеры для движения цены]

Верни ТОЛЬКО текст поста без лишних комментариев.
"""

  payload = {
      "contents": [{"parts": [{"text": prompt}]}],
      "generationConfig": {"temperature": 0.3},
  }

  for model_name in FALLBACK_MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    print(f"Пробуем сгенерировать пост через {model_name}...")

    try:
      res = requests.post(
          url,
          json=payload,
          headers={"Content-Type": "application/json"},
          timeout=(5, 30),
      )

      if res.status_code == 200:
        data = res.json()
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Успешный ответ от {model_name}!")

        full_post = (
            f"{ai_text.strip()}\n\n"
            f"───────────────────\n"
            f"🔗 Источник: {link}"
        )
        return full_post
      else:
        print(
            f" Модель {model_name} ответила с кодом {res.status_code}. Пробуем"
            " следующую..."
        )

    except requests.exceptions.Timeout:
      print(f"{model_name} превысила время ожидания (таймаут). Скипаем...")
    except Exception as e:
      print(f"Ошибка при запросе к {model_name}: {e}")

  return None