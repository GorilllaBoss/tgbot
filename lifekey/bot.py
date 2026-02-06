import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from openai import OpenAI

LIFEKEY_BOT_TOKEN = os.getenv("LIFEKEY_BOT_TOKEN") or os.getenv("BOT_TOKEN")
LIFEKEY_CHAT_ID = int(os.getenv("LIFEKEY_CHAT_ID", "0"))
LIFEKEY_OPENROUTER_KEY = os.getenv("LIFEKEY_OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY")

bot = None
dp = Dispatcher()
client = OpenAI(api_key=LIFEKEY_OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")

ASTRO_PROMPT = (
    "Ты астролог-ассистент. Дай краткий прогноз дня для человека:"
    " настроение, работа, отношения, энергия."
    " Стиль: конкретно, без воды, 4-6 пунктов."
)

NUMERO_PROMPT = (
    "Ты нумеролог-ассистент. По дате рождения и цели дай краткий разбор:"
    " сильные стороны, риски, и 3 практичных шага на день."
)

POST_PROMPT = (
    "Сделай короткий пост для канала LifeKey:"
    " астрология + нумерология + мотивация действия."
    " 3-5 строк, с эмодзи и финальным призывом к действию."
)


def ask_ai(system_text: str, user_text: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
            max_tokens=400,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print("LIFEKEY AI ERROR:", e)
        return "⚠️ Сервис временно недоступен. Попробуй позже."


@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("LifeKey активирован 🔮\nКоманды: /astro /numero")


@dp.message(Command("astro"))
async def astro(msg: Message):
    query = msg.text.replace("/astro", "", 1).strip() or "общий прогноз на сегодня"
    answer = ask_ai(ASTRO_PROMPT, query)
    await msg.answer(answer)


@dp.message(Command("numero"))
async def numero(msg: Message):
    query = msg.text.replace("/numero", "", 1).strip() or "дата: 01.01.2000, цель: фокус и доход"
    answer = ask_ai(NUMERO_PROMPT, query)
    await msg.answer(answer)


@dp.message()
async def chat(msg: Message):
    if not msg.text:
        return

    text = msg.text.lower()
    if "астро" in text or "гороскоп" in text:
        await msg.answer(ask_ai(ASTRO_PROMPT, msg.text))
        return
    if "нумеро" in text or "числ" in text:
        await msg.answer(ask_ai(NUMERO_PROMPT, msg.text))
        return

    await msg.answer(ask_ai("Ты ассистент LifeKey: астрология + нумерология + практические советы.", msg.text))


async def autopost_loop():
    sent_marks = set()
    while True:
        now = datetime.now()
        mark = now.strftime("%Y-%m-%d %H:%M")

        if LIFEKEY_CHAT_ID and now.hour in {9, 21} and now.minute == 0 and mark not in sent_marks:
            post = ask_ai(POST_PROMPT, f"Дата: {now.date().isoformat()}")
            try:
                if bot:
                    await bot.send_message(LIFEKEY_CHAT_ID, post)
                print("LIFEKEY AUTPOST: sent", mark)
            except Exception as e:
                print("LIFEKEY AUTPOST ERROR:", e)
            sent_marks.add(mark)

        if len(sent_marks) > 2000:
            sent_marks = set(sorted(sent_marks)[-500:])

        await asyncio.sleep(20)


async def main():
    global bot
    if not LIFEKEY_BOT_TOKEN:
        raise RuntimeError("LIFEKEY_BOT_TOKEN (or BOT_TOKEN) is not set")
    if not LIFEKEY_OPENROUTER_KEY:
        raise RuntimeError("LIFEKEY_OPENROUTER_KEY (or OPENROUTER_API_KEY) is not set")
    if not LIFEKEY_CHAT_ID:
        print("LIFEKEY warning: LIFEKEY_CHAT_ID is not set, autopost disabled")

    bot = Bot(token=LIFEKEY_BOT_TOKEN)

    asyncio.create_task(autopost_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
