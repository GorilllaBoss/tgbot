import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import OpenAI
import prompts
from config import (
    BOT_TOKEN,
    OPENROUTER_API_KEY,
    POSTS_FILE,
    DAILY_POST_CHAT_ID,
    POSTS_PER_DAY_MIN,
    POSTS_PER_DAY_MAX,
    POST_TIME_START,
    POST_TIME_END,
    AI_CHAT_ID,
    AI_POST_PROMPT
)

# =======================
# INIT
# =======================
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# =======================
# MEMORY (MULTI USER)
# =======================
BASE_MEMORY = "data/user_memory"
os.makedirs(BASE_MEMORY, exist_ok=True)

def user_dir(user_id: int):
    base = f"{BASE_MEMORY}/{user_id}"
    os.makedirs(f"{base}/raw", exist_ok=True)
    os.makedirs(f"{base}/daily", exist_ok=True)
    return base

# =======================
# JSON HELPERS
# =======================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =======================
# RAW MEMORY (TODAY)
# =======================
def remember(user_id: int, text: str):
    base = user_dir(user_id)
    today = datetime.now().date().isoformat()
    path = f"{base}/raw/{today}.json"

    data = {"date": today, "items": []}
    if os.path.exists(path):
        data = load_json(path, data)

    data["items"].append(text)
    save_json(path, data)

def load_today_raw(user_id: int, limit=20) -> str:
    base = user_dir(user_id)
    today = datetime.now().date().isoformat()
    path = f"{base}/raw/{today}.json"
    if not os.path.exists(path):
        return ""
    data = load_json(path, {})
    return "\n".join(data.get("items", [])[-limit:])

# =======================
# DAILY MEMORY
# =======================
def load_today_daily(user_id: int) -> str:
    base = user_dir(user_id)
    today = datetime.now().date().isoformat()
    path = f"{base}/daily/{today}.txt"
    if not os.path.exists(path):
        return ""
    return open(path, "r", encoding="utf-8").read()

def build_daily_from_raw(user_id: int, date: str):
    base = user_dir(user_id)
    raw_path = f"{base}/raw/{date}.json"
    if not os.path.exists(raw_path):
        return

    raw = load_json(raw_path, {})
    raw_text = "\n".join(raw.get("items", []))

    prompt = f"""
Ты — система формирования долгосрочной памяти пользователя.

Твоя задача — проанализировать ВЕСЬ текст целиком
и зафиксировать ТОЛЬКО устойчивые, долгосрочно значимые факты о пользователе.

Работай строго как аналитик памяти, а не как собеседник.

────────────────
ЧТО НУЖНО СДЕЛАТЬ
────────────────

1. Выдели ключевую информацию о пользователе, представляющую долгосрочную ценность.
2. Отделяй факты от эмоций (эмоции НЕ фиксируй).
3. Фиксируй только то, что:
   - повторялось
   - явно подтверждено
   - логически следует из поведения

4. Если пользователь:
   - противоречит сам себе
   - отрицает ранее сказанное
   - меняет позицию  
   → ОБЯЗАТЕЛЬНО зафиксируй это как факт.

────────────────
ОБЯЗАТЕЛЬНО ИЩИ И ФИКСИРУЙ
────────────────

ФИЗИКА:
- рост
- вес
- цель по весу
- явные ограничения организма

ПИТАНИЕ:
- проблемы с аппетитом
- сложности с объёмом еды
- ошибки или заблуждения
- отрицание рекомендаций

ТРЕНИРОВКИ:
- тип тренировок (силовые / кардио)
- частота
- отношение к тренировкам

ПСИХОЛОГИЯ:
- дисциплина / лень
- отношение к усилию
- реакция на жёсткость

СТИЛЬ ОБЩЕНИЯ:
- жёсткий / мягкий
- коротко / подробно
- запрос на изменение стиля

ПРОТИВОРЕЧИЯ:
- если пользователь говорит «А», а позже «не А» — зафиксируй

────────────────
СТРОГО ЗАПРЕЩЕНО
────────────────

- домысливать
- смягчать формулировки
- объяснять
- советовать
- писать диалоги
- пересказывать ход разговора

────────────────
ПРАВИЛА ВЫВОДА
────────────────

- кратко
- по пунктам
- максимум 10–12 пунктов
- только факты
- без эмоций
- без выводов
- ...

ЛОГИ:
{raw_text}
"""

    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    daily_text = resp.choices[0].message.content.strip()
    with open(f"{base}/daily/{date}.txt", "w", encoding="utf-8") as f:
        f.write(daily_text)

# =======================
# NIGHT TASK (00:00)
# =======================
async def daily_memory_loop():
    last = None
    while True:
        now = datetime.now()
        if now.hour == 0 and last != now.date():
            yesterday = (now.date() - timedelta(days=1)).isoformat()
            for uid in os.listdir(BASE_MEMORY):
                build_daily_from_raw(uid, yesterday)
            last = now.date()
        await asyncio.sleep(60)

# =======================
# COMMANDS
# =======================
@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("Я Gorilla 🦍")

# =======================
# MAIN HANDLER
# =======================
@dp.message()
async def handle(msg: types.Message):
    if msg.chat.type != "private":
        return

    user_id = msg.from_user.id
    text = msg.text.strip()

    remember(user_id, f"USER: {text}")

    messages = [
        {
            "role": "system",
            "content": prompts.GORILLA + """
ВАЖНО:
Если вопрос касается фактов из памяти (рост, вес, цели),
отвечай ФАКТОМ напрямую, без философии.
"""
        }
    ]

    daily = load_today_daily(user_id)
    if daily:
        messages.append({
            "role": "system",
            "content": f"АДАПТИВНАЯ ПАМЯТЬ (ФАКТЫ):\n{daily}"
        })

    raw = load_today_raw(user_id)
    if raw:
        messages.append({
            "role": "system",
            "content": f"КОНТЕКСТ ДНЯ:\n{raw}"
        })

    messages.append({"role": "user", "content": text})

    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0.4,
        max_tokens=300
    )

    answer = resp.choices[0].message.content
    remember(user_id, f"BOT: {answer}")
    await msg.answer(answer)

# =======================
# AUTOPST (ФАЙЛ)
# =======================
def load_posts():
    return load_json(POSTS_FILE, {"posts": []})

def save_posts(data):
    save_json(POSTS_FILE, data)

def get_random_post():
    data = load_posts()
    posts = data.get("posts", [])
    if not posts:
        return "⚠️ Нет постов"

    unused = [p for p in posts if not p.get("used")]
    if not unused:
        for p in posts:
            p["used"] = False
        unused = posts

    post = random.choice(unused)
    post["used"] = True
    save_posts(data)
    return post["text"]

def generate_schedule():
    count = random.randint(POSTS_PER_DAY_MIN, POSTS_PER_DAY_MAX)
    times = set()
    while len(times) < count:
        h = random.randint(POST_TIME_START, POST_TIME_END - 1)
        m = random.randint(0, 59)
        times.add(f"{h:02d}:{m:02d}")
    return sorted(times)

async def daily_post_loop():
    today = None
    plan = []
    sent = set()

    while True:
        now = datetime.now()

        if today != now.date():
            today = now.date()
            plan = generate_schedule()
            sent.clear()
            print("AUTOPST PLAN:", plan)

        t = now.strftime("%H:%M")
        if t in plan and t not in sent:
            try:
                post = get_random_post()
                print("AUTOPST SEND:", t)
                await bot.send_message(DAILY_POST_CHAT_ID, post)
                sent.add(t)
            except Exception as e:
                print("AUTOPST ERROR:", e)

        await asyncio.sleep(10)

# =======================
# AI POSTS (ОСТАВЛЕНО)
# =======================
async def ai_post_loop():
    while True:
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "system", "content": AI_POST_PROMPT}],
                temperature=0.9,
                max_tokens=200
            )

            text = resp.choices[0].message.content

            # 🔒 ЗАЩИТА
            if not text or not text.strip():
                print("AI_POST SKIPPED: empty response")
                await asyncio.sleep(60 * 10)
                continue

            text = text.strip()
            await bot.send_message(AI_CHAT_ID, text)

        except Exception as e:
            print("AI_POST ERROR:", e)

        await asyncio.sleep(60 * 60 * 6)

# =======================
# RUN
# =======================
async def main():
    asyncio.create_task(daily_memory_loop())
    asyncio.create_task(daily_post_loop())
    asyncio.create_task(ai_post_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
