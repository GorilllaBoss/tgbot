# tgbot

Запуск всех ботов в одном окне через лаунчер, без изменения логики самих ботов.

## Установка
```bash
python -m pip install -r requirements.txt
```

## Запуск
```bash
python run_all_bots.py
```

## `.env` (в корне репозитория)
```env
RUN_GORILLA=1
RUN_GONKAAI=1
RUN_LIFEKEY=0
LIFEKEY_ENTRY=lifekey/bot.py

BOT_TOKEN=
OPENROUTER_API_KEY=

GONKA_API_KEY=
CMC_API_KEY=
CHANNEL_ID=
POST_TIME_1=09:00
POST_TIME_2=18:00

LIFEKEY_BOT_TOKEN=
LIFEKEY_OPENROUTER_KEY=
LIFEKEY_CHAT_ID=
```

## Важно
- Если запускаете `Gorilla` и `LifeKey` одновременно — используйте **разные BOT_TOKEN**, иначе Telegram вернет `Conflict`.
- По умолчанию `RUN_LIFEKEY=0`, чтобы не словить конфликт токенов при первом запуске.
