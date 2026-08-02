import json
import os
import sys
import time

# Настройка UTF-8 вывода для Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from bot import send_to_telegram
from data_fetcher import fetch_top10_news, get_advanced_coin_metrics
from llm_writer import generate_post_final

# Файл локальной базы данных для опубликованных новостей
DB_FILE = "published_history.json"
CHECK_INTERVAL_SECONDS = 900  # Интервал проверки: 15 минут (900 сек)


def load_published_urls() -> set:
    """Загружает список уже опубликованных ссылок из JSON."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"[ОШИБКА] Ошибка чтения {DB_FILE}: {e}")
            return set()
    return set()


def save_published_url(url: str):
    """Сохраняет новую ссылку в JSON."""
    urls = load_published_urls()
    urls.add(url)
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(list(urls), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ОШИБКА] Ошибка сохранения в {DB_FILE}: {e}")


def get_news_url(item: dict) -> str:
    """Безопасно извлекает URL статьи из словаря новости."""
    return item.get("link") or item.get("url") or item.get("guid") or ""


def run_pipeline():
    """Один цикл проверки и публикации."""
    print("\n--------------------------------------------------")
    print(f"[{time.strftime('%H:%M:%S')}] Запуск нового цикла проверки новостей...")

    # 1. Загружаем историю отправленного
    published_urls = load_published_urls()

    # 2. Собираем новости
    print("[1/4] Запрашиваем RSS-ленты...")
    news_list = fetch_top10_news(limit=10)
    print(f"Собрано релевантных новостей: {len(news_list)}")

    if not news_list:
        print("Подходящих новостей пока нет.")
        return

    # 3. Фильтруем: ищем первую НОВУЮ новость
    target_news = None
    target_url = ""
    for item in news_list:
        url = get_news_url(item)
        if url and url not in published_urls:
            target_news = item
            target_url = url
            break

    if not target_news:
        print("Все свежие новости уже опубликованы. Ждем следующих...")
        return

    ticker = target_news.get("coin", "BTCUSDT")
    print(f"Найдена НОВАЯ новость [{target_news.get('raw_coin')}]: {target_news.get('title')}")

    # 4. Запрашиваем метрики Bybit
    print(f"[2/4] Запрашиваем метрики Bybit V5 для {ticker}...")
    market_metrics = get_advanced_coin_metrics(ticker)

    # 5. Генерация через Gemini
    print("[3/4] Генерируем аналитический разбор через Gemini...")
    post_text = generate_post_final(
        news_item=target_news, market_metrics=market_metrics
    )

    # 6. Отправка в Telegram
    if post_text:
        print("[4/4] Отправляем пост в Telegram...")
        send_to_telegram(post_text)

        # Сохраняем ссылку в базу, чтобы не постить повторно
        if target_url:
            save_published_url(target_url)
            print("[УСПЕХ] Ссылка сохранена в базу данных!")
    else:
        print("[ОШИБКА] Не удалось сгенерировать пост.")


def main():
    print("Бот запущен в автоматическом фоновом режиме!")
    print(f"Интервал проверки: каждые {CHECK_INTERVAL_SECONDS // 60} минут.")

    while True:
        try:
            run_pipeline()
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] Ошибка в цикле работы: {e}")

        print(f"\nУходим в сон на {CHECK_INTERVAL_SECONDS // 60} минут...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()