# tgbot

Единый репозиторий с несколькими Telegram-ботами:
- `Gorilla_bot` — ассистент, память, автопостинг, AI-посты.
- `gonkaai` — крипто-ассистент, BTC/ETH, автопостинг.
- `lifekey` — опционально, подключается через `LIFEKEY_ENTRY`.

## Установка
```bash
python -m pip install -r requirements.txt
```

## Запуск в одном окне
```bash
python run_all_bots.py
```

### Переменные управления
- `RUN_GORILLA=1|0`
- `RUN_GONKAAI=1|0`
- `RUN_LIFEKEY=1|0`
- `LIFEKEY_ENTRY=lifekey/bot.py`

Если `lifekey` отсутствует в репозитории, лаунчер пропустит его и продолжит запуск остальных ботов.

## Частые проблемы
- `ModuleNotFoundError` (например, `apscheduler`) — обнови зависимости из `requirements.txt`.
- `AuthenticationError 401` в Gorilla — проверь `OPENROUTER_API_KEY` в `Gorilla_bot/config.py` или перенеси ключ в `.env`.
