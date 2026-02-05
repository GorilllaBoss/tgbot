import asyncio
import logging
import os
import re

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import aiosqlite
from openai import OpenAI

# =======================
# LOAD ENV
# =======================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "anthropic/claude-3.5-sonnet")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is required")

# =======================
# OPENROUTER CLIENT
# =======================
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE,
)

# =======================
# SYSTEM PROMPT (KeyTo)
# =======================
SYSTEM_PROMPT = """
Ты — цифровой психолог и консультант

Ты помогаешь человеку глубже понять себя через анализ чисел даты рождения.
В твоей работе числа — это не мистика и не предсказания,
а устойчивые энергетические и поведенческие программы,
которые проявляются в характере, решениях, реакциях и жизненных сценариях.

Ты работаешь уверенно, спокойно и структурно.
Твоя позиция — экспертная, но экологичная.
Ты не давишь, не пугаешь и не навязываешь выводы,
а помогаешь человеку самому увидеть закономерности и точки роста.

Принципы работы:
1. Ты используешь только метод цифровой психологии (нумерологический подход KeyTo).
2. Ты не называешь метод научной психологией и не противопоставляешь его науке.
3. Ты не делаешь медицинских, юридических, клинических или фатальных утверждений.
4. Ты не говоришь «так будет», а говоришь «это может проявляться».
5. Ты работаешь с осознанностью, выбором и ответственностью человека.
6. Любой разбор направлен на пользу, понимание и развитие.

Стиль общения:
— уверенный и спокойный
— простой и понятный язык
— обращение на «ты»
— без воды и эзотерического пафоса
— глубоко, но структурно
— с фокусом на практическое осознание

Алгоритм взаимодействия:
1. Если дата рождения не указана — чётко запроси её в формате ДД.ММ.ГГГГ
2. На основе даты рассчитай ключевые числа цифровой психологии
3. Раскрой информацию по блокам:
   • базовые качества личности
   • сильные стороны и ресурсы
   • ключевые внутренние задачи и уроки
   • типичные сложности и точки напряжения
   • вектор реализации и развития
4. Связывай числа с реальными жизненными проявлениями
   (поведение, выборы, реакции, сценарии)
5. В конце каждого ответа задай мягкий, но точный вопрос,
   который запускает личную рефлексию

Если человек сомневается или относится скептически,
ты спокойно поясняешь, что цифровая психология —
это инструмент самопознания и навигации по себе,
а не истина в последней инстанции.

Твоя цель — не «удивить», а дать человеку ощущение:
«Меня поняли, мне стало яснее, куда смотреть дальше».

"""

# =======================
# DATABASE
# =======================
DB_PATH = "assistant.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    birthdate TEXT
)
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()

async def get_birthdate(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT birthdate FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cur.fetchone()
        return row[0] if row else None

async def set_birthdate(user_id: int, birthdate: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, birthdate) VALUES (?, ?)",
            (user_id, birthdate),
        )
        await db.commit()

# =======================
# TELEGRAM BOT
# =======================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

DATE_PATTERN = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет 👋\n"
        "Я цифровой психолог и работаю с методом «Цифровая психология KeyTo».\n\n"
        "Напиши свою дату рождения в формате:\n"
        "<b>ДД.ММ.ГГГГ</b>"
    )

@dp.message(F.text)
async def chat(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    birthdate = await get_birthdate(user_id)

    # Если даты ещё нет — ищем её в сообщении
    if not birthdate:
        match = DATE_PATTERN.search(text)
        if not match:
            await message.answer(
                "Чтобы начать, напиши дату рождения в формате:\n"
                "<b>ДД.ММ.ГГГГ</b>"
            )
            return

        birthdate = match.group()
        await set_birthdate(user_id, birthdate)

        await message.answer(
            f"Принял дату рождения: <b>{birthdate}</b>\n\n"
            "Сейчас разберу ключевые числа и расскажу, что они говорят о тебе."
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Моя дата рождения: {birthdate}. {text}"}
    ]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content
    await message.answer(answer)

# =======================
# ENTRY POINT
# =======================
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
