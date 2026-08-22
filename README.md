# GOLD FUNDAMENTAL MASTER 🏛️🏆

**GOLD FUNDAMENTAL MASTER** — это отказоустойчивая аналитическая платформа фундаментального анализа для золота (XAU/USD). Платформа работает 24/7 в автономном режиме в облаке и включает FastAPI Бэкенд, PostgreSQL, Redis, Telegram Бота (`aiogram` 3.x) и Telegram Mini App (React + TypeScript + Vite + Tailwind CSS) в институциональном стиле Wall Street Terminal.

> ⚠️ **IMPORTANT / СТРОГОЕ ТРЕБОВАНИЕ**:
> В данном проекте **ПОЛНОСТЬЮ ОТСУТСТВУЕТ ТЕХНИЧЕСКИЙ АНАЛИЗ**.
> В системе не используются и не допускаются: RSI, MACD, EMA/SMA, VWAP, паттерны свечей, уровни поддержки/сопротивления, ордерблоки, ликвидность, смарта-мани и фейковые вероятности (вида "87% bullish").
> Анализ базируется **ИСКЛЮЧИТЕЛЬНО** на фундаментальных драйверах золота.

---

## 🌟 1. Ключевые возможности

1. **4 Независимых горизонта анализа**:
   - **MONTH (1 Месяц)**: Режим ФРС, реальные доходности Treasuries, инфляционный тренд, резервы ЦБ, ETF.
   - **WEEK (1 Неделя)**: Календарь макрособытий недели, спикеры ФРС, геополитика.
   - **DAY (1 День)**: Календарь текущего дня, индексы макро-сюрпризов ($Surprise = Actual - Forecast$), овернайт новости.
   - **SESSION (Азия, Лондон, Нью-Йорк)**: Оперативный фундаментальный срез текущей торговой сессии.

2. **Фундаментальные движки (Quantitative Engines)**:
   - **Macro Surprise Engine**: Расчет количественного сюрприза экономических релизов (CPI, NFP, GDP).
   - **USD Engine**: Контекстуальная оценка доллара США (разграничение Hawkish Fed USD strength vs Geopolitical Safe-Haven demand).
   - **Yield & Real Yield Engine**: Анализ 10Y TIPS Real Yields (инфляционные ожидания vs номинальные ставки).
   - **Fed Stance Engine**: Классификация риторики ФРС (Hawkish, Dovish, Neutral, Mixed).
   - **News & Geopolitics Engine**: Фильтрация релевантности и оценки риска.

3. **OpenRouter AI Gateway**:
   - Безопасная генерация базовых и альтернативных сценариев, а также условий отмены (Invalidation) через OpenRouter API.
   - Строгая проверка ответа JSON через Pydantic.
   - Автоматический фоллбэк на запасные модели (например, `meta-llama/llama-3.3-70b-instruct`).
   - Кэширование запросов в Redis и контроль дневного бюджета запросов (`LLM_DAILY_REQUEST_LIMIT`).

4. **Telegram Mini App (Wall Street Terminal Style)**:
   - Верхняя **однострочная интерактивная лента горизонтов**: `MONTH | WEEK | DAY | ASIA | LONDON | NEW YORK` (с поддержкой горизонтального скролла на мобильных).
   - Плотная информативная сетка драйверов (USD, Fed, Real Yields, Macro, Geopolitics, Demand).
   - Валидация подписи Telegram WebApp `initData` по стандарту HMAC-SHA256.

5. **Режим автономной работы (`MOCK_MODE=true`)**:
   - Проект может работать 100% автономно без подключенных платных внешних API в режиме демо-данных.

---

## 🏗️ 2. Архитектура Продукта

```
Telegram User
      |
      +--------------------+
      |                    |
      v                    v
Telegram Bot         Telegram Mini App (Vite+React+Tailwind)
(aiogram 3.x)         (Wall Street Terminal Style)
      |                    |
      +---------+----------+
                |
                v
          FastAPI Backend (Python 3.11)
                |
       +--------+--------+
       |        |        |
       v        v        v
 PostgreSQL  Redis    Async Scheduler (APScheduler)
 (DB Storage) (Cache)    |
                         v
                   Data Collectors (Forex Factory, Fed, Yields, USD)
                         |
                         v
                   Fundamental Engine (Macro, Surprises, Scenarios)
                         |
                         v
                   OpenRouter AI Analysis (Pydantic JSON)
                         |
                         v
                  Telegram Alerts (Deduplicated)
```

---

## 🚀 3. Быстрый запуск в Docker

### Шаг 1. Клонирование и настройка окружения
```bash
git clone https://github.com/your-org/gold-fundamental-master.git
cd gold-fundamental-master
cp .env.example .env
```

### Шаг 2. Запуск контейнеров через Docker Compose
```bash
docker-compose up --build -d
```

Сервисы будут доступны по следующим адресам:
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Telegram Mini App Frontend**: http://localhost:80

---

## ⚙️ 4. Переменные Окружения (`.env`)

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `MOCK_MODE` | Включение режима демо-данных без живых ключей | `true` |
| `DATABASE_URL` | Подключение к PostgreSQL | `postgresql+asyncpg://postgres:postgres@db:5432/gold_fundamental` |
| `REDIS_URL` | Подключение к Redis | `redis://redis:6379/0` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram Бота | `1234567890:ABC...` |
| `TELEGRAM_WEBAPP_URL` | URL развернутого Mini App | `https://your-domain.com` |
| `OPENROUTER_API_KEY` | Ключ API OpenRouter | `sk-or-v1-...` |
| `OPENROUTER_MODEL` | Основная модель LLM | `google/gemini-2.0-flash-001` |
| `OPENROUTER_FALLBACK_MODEL` | Запасная модель LLM | `meta-llama/llama-3.3-70b-instruct` |
| `LLM_DAILY_REQUEST_LIMIT` | Дневной бюджет запросов к LLM | `100` |
| `SESSION_ASIA_OPEN` | UTC время открытия Азиатской сессии | `00:00` |
| `SESSION_LONDON_OPEN` | UTC время открытия Лондонской сессии | `08:00` |
| `SESSION_NEW_YORK_OPEN` | UTC время открытия Нью-Йоркской сессии | `13:00` |

---

## 🧪 5. Запуск Тестов

Для проверки работоспособности всех макро-движков и контроля отсутствия технического анализа:

```bash
python scripts/run_tests.py
```

---

## ☁️ 6. Развертывание на Облачные Платформы (Deployment)

Проект подготовлен для деплоя на любую Docker-совместимую облачную платформу:

### Railway / Render / Fly.io / VPS
1. Создайте сервис PostgreSQL и Redis на целевой платформе.
2. Скопируйте переменные из `.env.example` в настройки переменных окружения сервиса.
3. Задеплойте репозиторий через `docker-compose.yml` или подключите `Dockerfile` бэкенда и фронтенда.
4. Настройте HTTPS домен для Telegram WebApp и укажите его в `TELEGRAM_WEBAPP_URL`.

---

## 🔒 7. Production deployment (Render)

The bot is started inside the FastAPI lifespan. Do not deploy `bot/bot.py` as a
second worker: two long-polling consumers will conflict and Telegram updates
will be lost or repeatedly retried. The supplied `render.yaml` keeps one web
process and runs `alembic upgrade head` before Uvicorn starts.

Before the first production deploy, set these **secret environment variables**
in Render (never commit them):

- `DATABASE_URL` — Render PostgreSQL URL; `postgres://` and `postgresql://`
  are converted to `postgresql+asyncpg://` automatically.
- `SECRET_KEY` — a new cryptographically random secret.
- `TELEGRAM_BOT_TOKEN` — a newly rotated BotFather token.
- `TELEGRAM_WEBAPP_URL` and `CORS_ALLOWED_ORIGINS` — the exact HTTPS Netlify
  origin.

Also set `BACKEND_URL` to the public backend HTTPS URL, `MOCK_MODE=true` for
demo data or `false` only after live data providers have been configured. The
application refuses an unsafe production configuration instead of silently
starting with a local database, wildcard CORS, or a missing bot token.

Use `/health` for platform liveness and `/ready` for dependency readiness.
`/api/v1/system/status` reports `MOCK`, `OFFLINE`, or `ONLINE` truthfully; it
does not claim that an unconfigured service is online.

## 📄 8. Лицензия
Проект распространяется под лицензией [MIT](LICENSE).
