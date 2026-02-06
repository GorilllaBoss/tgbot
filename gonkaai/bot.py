import os
import asyncio
import httpx
from datetime import datetime
from openai import OpenAI

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message


def _int_env(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


BOT_TOKEN = os.getenv("BOT_TOKEN")
CMC_API_KEY = os.getenv("CMC_API_KEY")
CHANNEL_ID = _int_env("CHANNEL_ID", 0)

POST_TIME_1 = os.getenv("POST_TIME_1", "09:00")
POST_TIME_2 = os.getenv("POST_TIME_2", "18:00")

GONKA_API_KEY = os.getenv("GONKA_API_KEY")

CMC_URL = "https://pro-api.coinmarketcap.com/v1"

bot = None
dp = Dispatcher()
router = Router()
ai_client = None

MODEL_NAME = "qwen/qwen3-235b-a22b-instruct-2507-fp8"


def _parse_time(value: str):
    h, m = value.split(":")
    return int(h), int(m)


def _is_time_match(now, target: str) -> bool:
    h, m = _parse_time(target)
    return now.hour == h and now.minute == m


async def get_crypto(symbol="BTC"):
    url = f"{CMC_URL}/cryptocurrency/quotes/latest"

    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": symbol, "convert": "USD"}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params)
        data = r.json()

    q = data["data"][symbol]["quote"]["USD"]

    return {
        "price": q["price"],
        "change24": q["percent_change_24h"],
        "volume": q["volume_24h"],
    }


def calc_support(price):
    return round(price * 0.97), round(price * 0.94)


def detect_trend(change):
    if change > 2:
        return "📈 Сильный рост"
    elif change > 0:
        return "📈 Рост"
    elif change > -2:
        return "📉 Коррекция"
    else:
        return "📉 Снижение"


async def ai_answer(text):
    if ai_client is None:
        return "⚠️ GONKA_API_KEY не задан. AI-режим недоступен."

    try:
        resp = ai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты универсальный ИИ-ассистент. "
                        "Помогаешь в любых вопросах: технологии, обучение, "
                        "бизнес, криптовалюты, повседневные задачи. "
                        "Отвечай понятно, кратко и полезно."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )

        return resp.choices[0].message.content
    except Exception as e:
        print("GONKA AI ERROR:", e)
        return "⚠️ Ошибка AI-провайдера. Попробуй позже."


async def build_market_post():
    data = await get_crypto("BTC")

    price = data["price"]
    change = data["change24"]
    volume = data["volume"]

    s1, s2 = calc_support(price)
    trend = detect_trend(change)

    if change >= 3:
        signal = "🟢 Бычий импульс"
    elif change <= -3:
        signal = "🔴 Давление продавцов"
    else:
        signal = "🟡 Боковое движение"

    text = (
        "🚀 *BTC Market Brief*\n"
        "━━━━━━━━━━━━━━\n"
        f"💰 *Цена:* `${price:,.0f}`\n"
        f"📈 *24ч:* `{change:+.2f}%`\n"
        f"📊 *Объём:* `${volume:,.0f}`\n\n"
        f"{trend} | {signal}\n\n"
        "🧱 *Уровни поддержки*\n"
        f"• S1: `{s1:,}`\n"
        f"• S2: `{s2:,}`\n\n"
        "📌 *Идея на день:*\n"
        "Следим за реакцией цены у S1/S2 и работаем только по подтверждению.\n\n"
        "#BTC #crypto #trading"
    )

    return text


async def autopost():
    if bot is None or CHANNEL_ID == 0:
        return

    try:
        text = await build_market_post()
        await bot.send_message(CHANNEL_ID, text, parse_mode="Markdown")
        print("Post sent")
    except Exception as e:
        print("Autopost error:", e)


async def scheduler_loop():
    sent_marks = set()

    while True:
        dt = datetime.now()
        mark = dt.strftime("%Y-%m-%d %H:%M")

        if mark not in sent_marks and (
            _is_time_match(dt, POST_TIME_1)
            or _is_time_match(dt, POST_TIME_2)
        ):
            await autopost()
            sent_marks.add(mark)

        if len(sent_marks) > 2000:
            sent_marks = set(sorted(sent_marks)[-500:])

        await asyncio.sleep(20)


@router.message(Command("btc"))
async def btc(message: Message):
    data = await get_crypto("BTC")

    await message.answer(
        f"BTC: ${data['price']:,.2f}\n"
        f"Изменение 24ч: {data['change24']:.2f}%"
    )


@router.message(Command("eth"))
async def eth(message: Message):
    data = await get_crypto("ETH")

    await message.answer(
        f"ETH: ${data['price']:,.2f}\n"
        f"Изменение 24ч: {data['change24']:.2f}%"
    )


@router.message()
async def chat(message: Message):
    if not message.text:
        return

    text = message.text.lower()
    chat_type = message.chat.type

    if chat_type == "private":
        reply = await ai_answer(message.text)
        await message.answer(reply)
        return

    me = await bot.get_me()
    username = me.username.lower()

    mentioned = (
        f"@{username}" in text
        or "гонка" in text
        or "gonka" in text
    )

    if mentioned:
        reply = await ai_answer(message.text)
        await message.reply(reply)


async def main():
    global bot, ai_client

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set for gonkaai")

    if not CMC_API_KEY:
        print("Warning: CMC_API_KEY is not set, /btc and /eth may fail")
    if CHANNEL_ID == 0:
        print("Warning: CHANNEL_ID is not set, autopost will fail")
    if not GONKA_API_KEY:
        print("Warning: GONKA_API_KEY is not set, AI chat will return fallback message")

    bot = Bot(token=BOT_TOKEN)
    if GONKA_API_KEY:
        ai_client = OpenAI(
            base_url="https://api.gonkagate.com/v1",
            api_key=GONKA_API_KEY,
        )

    dp.include_router(router)
    asyncio.create_task(scheduler_loop())

    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
