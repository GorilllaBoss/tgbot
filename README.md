# tgbot

Единый репозиторий с несколькими Telegram-ботами:
- `Gorilla_bot` — ассистент, память, автопостинг, AI-посты.
- `gonkaai` — крипто-ассистент, BTC/ETH, автопостинг.
- `lifekey` — астролог + нумеролог + AI-автопостинг.

## Установка
```bash
python -m pip install -r requirements.txt
```

## Запуск в одном окне
```bash
python run_all_bots.py
```

### Переменные управления лаунчером
- `RUN_GORILLA=1|0`
- `RUN_GONKAAI=1|0`
- `RUN_LIFEKEY=1|0`
- `LIFEKEY_ENTRY=lifekey/bot.py`

### Переменные для LifeKey
- `LIFEKEY_BOT_TOKEN` (или fallback: `BOT_TOKEN`)
- `LIFEKEY_OPENROUTER_KEY` (или fallback: `OPENROUTER_API_KEY`)
- `LIFEKEY_CHAT_ID` (канал для автопостинга)

## Частые проблемы
- `ModuleNotFoundError` — установи зависимости командой выше.
- `AuthenticationError 401` в Gorilla/LifeKey — проверь API-ключ OpenRouter и доступность аккаунта.


## Важные условия запуска
- У `Gorilla` и `LifeKey` **должны быть разные BOT_TOKEN**, иначе будет `TelegramConflictError` (один токен не может иметь два long-polling процесса одновременно).
- Для `gonkaai` нужен `GONKA_API_KEY`, иначе AI-ответы в чате будут в fallback-режиме.
- Если запускаешь только одного бота, отключи остальные через `RUN_GORILLA/RUN_GONKAAI/RUN_LIFEKEY`.
