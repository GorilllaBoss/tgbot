# tgbot

Единый репозиторий с несколькими Telegram-ботами:
- `Gorilla_bot` — ассистент, память, автопостинг, AI-посты.
- `gonkaai` — крипто-ассистент, BTC/ETH, автопостинг.
- `lifekey` — опционально, подключается через `LIFEKEY_ENTRY`.

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
