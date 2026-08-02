# Crypto Pulse Agent

> Автономный Telegram-бот для мониторинга новостного фона криптотиры и генерации экспресс-аналитики.
<img width="1381" height="432" alt="image" src="https://github.com/user-attachments/assets/7d522059-439d-4462-b71d-d5dd684a37fd" />

Бот отслеживает RSS-ленты ведущих СМИ, подтягивает актуальные биржевые метрики с деривативного рынка Bybit (V5 API) и формирует структурированные обзоры с помощью Google Gemini API.

---

## Что делает

| Функция | Описание |
|---------|----------|
| **RSS-мониторинг** | Сканирует ленты Cointelegraph, CoinDesk, CryptoPotato и Decrypt |
| **Фильтрация по активам** | Автоматически находит упоминания ключевых монет (BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOGE, DOT, LINK), очищает текст от HTML-мусора и отсеивает дубликаты |
| **Биржевые метрики (Bybit V5 API)** | Параллельно с новостью запрашивает спотовые котировки, 24h объём, открытый интерес (OI), фандинг (Funding Rate) и сентимент трейдеров (Long/Short ratio) |
| **Генерация аналитики (LLM)** | Прогоняет новостной контекст и метрики через Gemini API с каскадной системой моделей |
| **Автоматика и дедупликация** | Работает в непрерывном цикле (проверка каждые 15 минут). Ведёт локальную базу отправленных новостей, исключая повторные публикации |
| **Публикация в Telegram** | Отправляет сформированный пост с клиповым заголовком, блоками разбора, прогнозом и ссылкой-источником для генерации превью |

---

<img width="1578" height="897" alt="image" src="https://github.com/user-attachments/assets/86210a07-bb15-4b65-83c0-af711f51ac6b" />


## Стек

- **Язык:** Python 3.10+
- **Данные и API:** `requests`, `feedparser`, `python-dotenv`
- **Аналитика и LLM:** Google Gemini API (v1beta REST)
- **Платформа:** Telegram Bot API, Bybit REST API v5

---

## Структура проекта

```
├── main.py                   # Главный пайплайн, оркестратор и бесконечный цикл
├── data_fetcher.py           # Парсер RSS-лент и модуль интеграции с API Bybit
├── llm_writer.py             # Генератор постов через Gemini API с fallback-моделями
├── bot.py                    # Модуль отправки сообщений в Telegram
├── config.py                 # Конфигурация, список монет, фильтры и ключи
├── run.bat                   # Скрипт быстрого запуска для Windows (UTF-8)
├── published_history.json    # Локальная БД опубликованных ссылок (создаётся автоматически)
├── requirements.txt          # Зависимости проекта
└── .env                      # Файл с приватными ключами окружения
```

---

## Как запустить

### 1. Клонирование и установка зависимостей

```bash
git clone <repo_url>
cd <repo_directory>
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта:

```env
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=@your_channel_id_or_chat_id
```

> ⚠️ **Важно:** Никогда не коммитьте файл `.env` в репозиторий. Он уже добавлен в `.gitignore`.

### 3. Запуск

**На Windows через `run.bat`:**
Двойной клик по файлу `run.bat`.

**Через консоль:**
```bash
python main.py
```

---

## Как это работает

1. Бот собирает свежие новости из RSS-лент крипто-СМИ
2. Фильтрует по ключевым монетам и удаляет дубликаты
3. Для найденной новости подтягивает актуальные метрики с Bybit
4. Передаёт новость + метрики в Gemini API для генерации аналитического разбора
5. Публикует готовый пост в Telegram-канал
6. Сохраняет ссылку в локальную базу и засыпает на 15 минут

---

## Fallback-модели Gemini

В проекте реализована каскадная система моделей для бесперебойной генерации:

```
gemini-3.6-flash  →  gemini-3.5-flash-lite  →  gemini-2.5-flash
```

Если одна модель недоступна по квоте или ошибке — бот автоматически переключается на следующую.

---

## Скриншоты

> - Пример сгенерированного поста в Telegram
<img width="629" height="927" alt="image" src="https://github.com/user-attachments/assets/0aca23b5-4fd6-4d0a-9d55-f42410ce5f1d" />
<img width="709" height="905" alt="image" src="https://github.com/user-attachments/assets/0a71aff4-e129-4023-9737-738dcb5a289e" />

---

## Лицензия

MIT

---

*Создано для автоматизации крипто-аналитики и демонстрации навыков работы с API, data pipelines и LLM.*
