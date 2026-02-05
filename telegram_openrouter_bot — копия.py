import asyncio
import logging
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import aiosqlite
from openai import OpenAI

# ================= ENV =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "anthropic/claude-3.5-sonnet")

# ================= OPENAI CLIENT =================
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

# ================= PROMPTS =================
ASTRO_ANALYSIS_PROMPT = """
Ты профессиональный астролог.

У тебя есть все данные для построения натальной карты.
Сделай последовательный разбор:

1. Солнце (характер, базовая мотивация)
2. Асцендент (стиль поведения, первое впечатление)
3. Луна (эмоции и внутренние реакции)
4. Сильные стороны карты
5. Зоны роста

Говори ясно, без мистики, без фатальных прогнозов.
После разбора задай вопрос:
«Хочешь перейти к текущим вопросам или разобрать один из пунктов глубже?»
"""

ASTRO_DIALOG_PROMPT = """
Ты астролог-консультант.

У тебя уже есть натальная карта пользователя.
Ты отвечаешь на вопросы, опираясь на неё.

Ты:
- помнишь данные карты
- не просишь их заново
- не пересобираешь карту
- ведёшь диалог спокойно и по делу
"""

NUMEROLOGY_ANALYSIS_PROMPT = """
Ты профессиональный нумеролог.

Ты работаешь по структурированному принципу, аналогично астрологу: анализ → интерпретация → выводы → рекомендации.

Роль:
- Нумеролог — специалист по числам, связанным с датой рождения и именем.
- Помогаешь понять сильные стороны, жизненные задачи, кармические уроки.

Последовательность разбора:
1. Число жизненного пути — предназначение и путь человека
2. Число судьбы (выражения) — таланты и потенциал
3. Число души — внутренние желания и мотивация
4. Число личности — как человек воспринимается окружающими
5. Кармические числа — уроки, зоны роста
6. Мастер-числа (11, 22, 33) — усиленные качества

Стиль ответа:
- ясный, логичный, последовательный
- без мистики и фатальных прогнозов
- с рекомендациями для осознанного выбора
"""

NUMEROLOGY_DIALOG_PROMPT = """
Ты нумеролог-консультант.

У тебя есть ключевые числа пользователя.
Отвечаешь на вопросы, опираясь на них.
Не пересчитываешь числа, помнишь данные и ведешь диалог спокойно.
"""

# ================= DB =================
DB_PATH = "assistant.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    mode TEXT,
    stage TEXT,
    astro_birthdate TEXT,
    astro_time TEXT,
    astro_place TEXT,
    summary TEXT
)
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        return await cur.fetchone()

async def save_user(data):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO users
            (user_id, mode, stage, astro_birthdate, astro_time, astro_place, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            data,
        )
        await db.commit()

# ================= UI =================
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌙 Астролог")],
        [KeyboardButton(text="🔢 Нумеролог")]
    ],
    resize_keyboard=True
)

# ================= BOT =================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================= ВАЛИДАЦИЯ =================
def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def validate_time(time_text):
    return bool(re.match(r"^([01]?\d|2[0-3]):([0-5]\d)$", time_text))

def validate_place(place_text):
    return len(place_text.split()) >= 2

# ================= HANDLERS =================
@dp.message(CommandStart())
async def start(message: Message):
    await save_user((message.from_user.id, None, None, None, None, None, None))
    await message.answer("Выбери формат 👇", reply_markup=keyboard)

# ===== ОБЪЕДИНЁННЫЙ FLOW =====
@dp.message(F.text)
async def unified_flow(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Нажми /start")
        return

    user_id, mode, stage, bdate, btime, place, summary = user
    text = message.text.strip()

    # ===== Выбор режима =====
    if text == "🌙 Астролог":
        await save_user((user_id, "astrology", "birthdate", None, None, None, None))
        await message.answer("Напиши дату рождения (ДД.MM.ГГГГ)")
        return
    if text == "🔢 Нумеролог":
        await save_user((user_id, "numerology", "birthdate", None, None, None, None))
        await message.answer("Напиши дату рождения (ДД.MM.ГГГГ)")
        return

    # ===== АСТРОЛОГ =====
    if mode == "astrology":
        if stage == "birthdate":
            if not validate_date(text):
                await message.answer("Неверный формат даты. Напиши в формате ДД.MM.ГГГГ")
                return
            await save_user((user_id, "astrology", "time", text, None, None, None))
            await message.answer("Принял. Теперь напиши время рождения (например 15:05)")
            return

        if stage == "time":
            if not validate_time(text):
                await message.answer("Неверный формат времени. Используй ЧЧ:ММ")
                return
            await save_user((user_id, "astrology", "place", bdate, text, None, None))
            await message.answer("Хорошо. Теперь напиши место рождения (город, страна)")
            return

        if stage == "place":
            if not validate_place(text):
                await message.answer("Пожалуйста, укажи город и страну (например: Москва Россия)")
                return
            await save_user((user_id, "astrology", "analysis", bdate, btime, text, None))
            prompt = f"Данные пользователя:\nДата: {bdate}\nВремя: {btime}\nМесто: {text}"
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ASTRO_ANALYSIS_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            analysis = response.choices[0].message.content
            await save_user((user_id, "astrology", "dialog", bdate, btime, text, analysis))
            await message.answer(analysis)
            return

        if stage == "dialog":
            dialog_prompt = f"Натальная карта пользователя:\n{summary}\n\nВопрос пользователя:\n{text}"
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ASTRO_DIALOG_PROMPT},
                    {"role": "user", "content": dialog_prompt},
                ],
            )
            await message.answer(response.choices[0].message.content)
            return

    # ===== НУМЕРОЛОГ =====
    if mode == "numerology":
        if stage == "birthdate":
            if not validate_date(text):
                await message.answer("Неверный формат даты. Напиши в формате ДД.MM.ГГГГ")
                return
            await save_user((user_id, "numerology", "dialog", text, None, None, None))
            prompt = f"Данные пользователя:\nДата рождения: {text}\n"
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": NUMEROLOGY_ANALYSIS_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            analysis = response.choices[0].message.content
            await save_user((user_id, "numerology", "dialog", text, None, None, analysis))
            await message.answer(analysis)
            return

        if stage == "dialog":
            dialog_prompt = f"Числа пользователя:\n{summary}\n\nВопрос пользователя:\n{text}"
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": NUMEROLOGY_DIALOG_PROMPT},
                    {"role": "user", "content": dialog_prompt},
                ],
            )
            await message.answer(response.choices[0].message.content)
            return

# ================= RUN =================
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
