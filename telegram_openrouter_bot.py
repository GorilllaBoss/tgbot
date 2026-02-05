# telegram_openrouter_bot.py
# Dialog bot (Astrology + Numerology) + Daily channel posts
# Bot answers ONLY in private chat and stays silent in groups/channels.
# Daily posts are sent to a channel/group at time defined in .env

import asyncio
import logging
import os
import re
import aiosqlite
import httpx
from datetime import datetime, timedelta

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ================= ENV =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "openai/gpt-4.1"

# where to send posts
POST_CHAT_ID = os.getenv("POST_CHAT_ID")

# post time (default 08:00)
POST_HOUR = int(os.getenv("POST_HOUR", "8"))
POST_MINUTE = int(os.getenv("POST_MINUTE", "0"))

# ================= DB =================
DB_PATH = "assistant.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    mode TEXT,
    stage TEXT,
    birthdate TEXT,
    time TEXT,
    place TEXT,
    summary TEXT,
    partner_birthdate TEXT,
    partner_time TEXT,
    partner_place TEXT
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

async def save_user(data):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data
        )
        await db.commit()

# ================= LLM =================
async def call_llm(system, user):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "LifeKeyBot",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                # allow fallback so posts never fail
                "provider": {
                    "order": ["openai", "anthropic"],
                    "allow_fallbacks": True
                }
            }
        )

        data = response.json()
        if "error" in data:
            raise RuntimeError(data["error"])

        return data["choices"][0]["message"]["content"]

# ================= PROMPTS =================
ASTRO_MAIN = """
Ты профессиональный астролог.
Сделай последовательный разбор:
1. Солнце
2. Асцендент
3. Луна
4. Сильные стороны
5. Зоны роста
Говори ясно, без мистики.
"""

NUM_MAIN = """
Ты профессиональный нумеролог.
Сделай разбор:
— число жизненного пути
— сильные стороны
— задачи
— рекомендации
Без мистики.
"""

# daily posts
ASTRO_DAILY_PROMPT = """
Сделай краткую астрологическую рекомендацию на день.
2–3 предложения, коротко и понятно.
"""

NUM_DAILY_PROMPT = """
Сделай краткую нумерологическую рекомендацию дня.
2–3 предложения с практическим советом.
"""

# ================= UI =================
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🌙 Астролог")], [KeyboardButton(text="🔢 Нумеролог")]],
    resize_keyboard=True
)

# ================= BOT =================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ================= DAILY POST =================
async def send_daily_post():
    if not POST_CHAT_ID:
        print("POST_CHAT_ID not set — post skipped")
        return

    today = datetime.now().strftime("%d.%m.%Y")

    astro_text = await call_llm(ASTRO_DAILY_PROMPT, f"Дата: {today}")
    num_text = await call_llm(NUM_DAILY_PROMPT, f"Дата: {today}")

    post = (
        f"🌅 Рекомендация дня • {today}\n\n"
        f"🌙 Астрология\n{astro_text}\n\n"
        f"🔢 Нумерология\n{num_text}"
    )

    await bot.send_message(int(POST_CHAT_ID), post)
    print("Daily post sent")


async def daily_scheduler():
    while True:
        now = datetime.now()
        target = now.replace(
            hour=POST_HOUR,
            minute=POST_MINUTE,
            second=0,
            microsecond=0
        )

        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep((target - now).total_seconds())
        await send_daily_post()

# ================= HANDLERS =================
@dp.message(CommandStart())
async def start(message: Message):
    # bot answers only in private chat
    if message.chat.type != "private":
        return

    await save_user((message.from_user.id, None, None, None, None, None, None, None, None, None))
    await message.answer("Привет 👋\nВыбери формат 👇", reply_markup=keyboard)


@dp.message(F.text == "🌙 Астролог")
async def astro_start(message: Message):
    if message.chat.type != "private":
        return

    await save_user((message.from_user.id, "astrology", "birthdate", None, None, None, None, None, None, None))
    await message.answer("Напиши дату рождения (ДД.ММ.ГГГГ)")


@dp.message(F.text == "🔢 Нумеролог")
async def num_start(message: Message):
    if message.chat.type != "private":
        return

    await save_user((message.from_user.id, "numerology", "birthdate", None, None, None, None, None, None, None))
    await message.answer("Напиши дату рождения (ДД.ММ.ГГГГ)")


@dp.message(F.text)
async def dialog(message: Message):
    # ignore groups/channels
    if message.chat.type != "private":
        return

    user = await get_user(message.from_user.id)
    if not user:
        return

    uid, mode, stage, bd, tm, pl, sm, pbd, ptm, ppl = user
    text = message.text.strip()

    if stage == "birthdate":
        await save_user((uid, mode, "time", text, None, None, None, None, None, None))
        await message.answer("Теперь время рождения")
        return

    if stage == "time":
        await save_user((uid, mode, "place", bd, text, None, None, None, None, None))
        await message.answer("Теперь место рождения")
        return

    if stage == "place":
        await save_user((uid, mode, "dialog", bd, tm, text, None, None, None, None))
        system = ASTRO_MAIN if mode == "astrology" else NUM_MAIN
        prompt = f"Дата: {bd}\nВремя: {tm}\nМесто: {text}"
        result = await call_llm(system, prompt)
        await save_user((uid, mode, "dialog", bd, tm, text, result, None, None, None))
        await message.answer(result)
        return

    system = ASTRO_MAIN if mode == "astrology" else NUM_MAIN
    prompt = f"Контекст:\n{sm}\n\nВопрос:\n{text}"
    result = await call_llm(system, prompt)
    await message.answer(result)

# ================= RUN =================
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    asyncio.create_task(daily_scheduler())

    print("USING MODEL:", OPENAI_MODEL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
