from typing import Dict, Any

message_templates: Dict[str, Dict[str, str]] = {
    'en': {
        'start': """👋 Hello! I'm a smart AI assistant.

I can help you with various tasks using powerful AI models:
• GPT-4 🤖 - Advanced language model
• Gemini ✨ - Google's latest AI
• GPT-4O 🔮 - Optimized GPT-4
• GPT-4O-mini 🎯 - Faster version
• Claude 3.5 Sonnet 🎭 - Anthropic's latest model
• Claude 3.5 Haiku 🎋 - Fast and efficient

Features:
• Multi-language support 🌐
• Image generation 🎨
• Smart conversations 💭

Use the buttons below to interact with me!""",
        'help': """🔍 <b>Available Commands:</b>

/start - Start bot
/help - Show this help
/about - About bot
/language - Change language
/model - Change AI model
/newtopic - Start new topic
/image - Generate image
/stats - Show chat statistics

You can also use the buttons below for quick access.""",
        'about': """🤖 <b>AI Assistant Bot</b>

This bot combines multiple powerful AI models:
• OpenAI GPT-4
• Google Gemini
• GPT-4O
• GPT-4O-mini
• Claude 3.5 Sonnet
• Claude 3.5 Haiku

Version: 2.0
Developer: @your_username""",
        'stats': """📊 <b>Chat Statistics</b>

Current model: {model}
Messages in history: {messages}/{max_messages}
Estimated tokens: {tokens}/{max_tokens}

Use /newtopic to clear history""",
        'new_topic': '🆕 Starting a new topic!',
        'image_prompt': '🎨 Please describe the image you want to generate:',
        'image_error': '❌ An error occurred during image generation:',
        'language_confirmation': "🌐 Language has been set to English",
        'language_selection': "🌍 Choose your language:",
        'processing': "⏳ Processing your request...",
        'error': "❌ An error occurred. Please try again later.",
        'model_switched_gpt4': "🤖 Switched to GPT-4 model",
        'model_switched_gemini': "✨ Switched to Gemini model",
        'model_switched_gpt4o': "🔮 Switched to GPT-4O model",
        'model_switched_gpt4o_mini': "🎯 Switched to GPT-4O-mini model",
        'model_switched_claude': "🎭 Switched to Claude 3.5 Sonnet model",
        'model_switched_claude_haiku': "🎋 Switched to Claude 3.5 Haiku model",
        'current_model': "Current model: {model}",
        'safety_error': """⚠️ I cannot process this request due to content safety guidelines.
Please rephrase your message to be more appropriate."""
    },
    'ru': {
        'start': """👋 Привет! Я умный ИИ-ассистент.

Я могу помочь с разными задачами, используя мощные модели ИИ:
• GPT-4 🤖 - Продвинутая языковая модель
• Gemini ✨ - Новейший ИИ от Google
• GPT-4O 🔮 - Оптимизированный GPT-4
• GPT-4O-mini 🎯 - Быстрая версия
• Claude 3.5 Sonnet 🎭 - Новейшая модель от Anthropic
• Claude 3.5 Haiku 🎋 - Быстрая и эффективная

Возможности:
• Поддержка разных языков 🌐
• Генерация изображений 🎨
• Умные диалоги 💭

Используйте кнопки ниже для взаимодействия!""",
        'help': """🔍 <b>Доступные команды:</b>

/start - Запустить бота
/help - Показать помощь
/about - О боте
/language - Сменить язык
/model - Сменить модель ИИ
/newtopic - Начать новую тему
/image - Создать изображение
/stats - Показать статистику чата

Также можно использовать кнопки ниже для быстрого доступа.""",
        'about': """🤖 <b>ИИ-Ассистент Бот</b>

Этот бот объединяет несколько мощных моделей ИИ:
• OpenAI GPT-4
• Google Gemini
• GPT-4O
• GPT-4O-mini
• Claude 3.5 Sonnet
• Claude 3.5 Haiku

Версия: 2.0
Разработчик: @your_username""",
        'stats': """📊 <b>Статистика чата</b>

Текущая модель: {model}
Сообщений в истории: {messages}/{max_messages}
Примерное количество токенов: {tokens}/{max_tokens}

Используйте /newtopic для очистки истории""",
        'new_topic': '🆕 Начинаем новую тему!',
        'image_prompt': '🎨 Пожалуйста, опишите изображение, которое хотите создать:',
        'image_error': '❌ Произошла ошибка при создании изображения:',
        'language_confirmation': "🌐 Язык изменён на русский",
        'language_selection': "🌍 Выберите язык:",
        'processing': "⏳ Обрабатываю ваш запрос...",
        'error': "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
        'model_switched_gpt4': "🤖 Переключено на модель GPT-4",
        'model_switched_gemini': "✨ Переключено на модель Gemini",
        'model_switched_gpt4o': "🔮 Переключено на модель GPT-4O",
        'model_switched_gpt4o_mini': "🎯 Переключено на модель GPT-4O-mini",
        'model_switched_claude': "🎭 Переключено на модель Claude 3.5 Sonnet",
        'model_switched_claude_haiku': "🎋 Переключено на модель Claude 3.5 Haiku",
        'current_model': "Текущая модель: {model}",
        'safety_error': """⚠️ Я не могу обработать этот запрос из-за правил безопасности.
Пожалуйста, перефразируйте сообщение."""
    },
    'ua': {
        'start': """👋 Привіт! Я розумний ІІ-асистент.

Я можу допомогти з різними завданнями, використовуючи потужні моделі ІІ:
• GPT-4 🤖 - Просунута мовна модель
• Gemini ✨ - Найновіший ІІ від Google
• GPT-4O 🔮 - Оптимізований GPT-4
• GPT-4O-mini 🎯 - Швидка версія
• Claude 3.5 Sonnet 🎭 - Найновіша модель від Anthropic
• Claude 3.5 Haiku 🎋 - Швидка та ефективна

Можливості:
• Підтримка різних мов 🌐
• Генерація зображень 🎨
• Розумні діалоги 💭

Використовуйте кнопки нижче для взаємодії!""",
        'help': """🔍 <b>Доступні команди:</b>

/start - Запустити бота
/help - Показати довідку
/about - Про бота
/language - Змінити мову
/model - Змінити модель ІІ
/newtopic - Почати нову тему
/image - Створити зображення
/stats - Показати статистику чату

Також можна використовувати кнопки нижче для швидкого доступу.""",
        'about': """🤖 <b>ІІ-Асистент Бот</b>

Цей бот поєднує кілька потужних моделей ІІ:
• OpenAI GPT-4
• Google Gemini
• GPT-4O
• GPT-4O-mini
• Claude 3.5 Sonnet
• Claude 3.5 Haiku

Версія: 2.0
Розробник: @your_username""",
        'stats': """📊 <b>Статистика чату</b>

Поточна модель: {model}
Повідомлень в історії: {messages}/{max_messages}
Приблизна кількість токенів: {tokens}/{max_tokens}

Використовуйте /newtopic для очищення історії""",
        'new_topic': '🆕 Починаємо нову тему!',
        'image_prompt': '🎨 Будь ласка, опишіть зображення, яке хочете створити:',
        'image_error': '❌ Сталася помилка при створенні зображення:',
        'language_confirmation': "🌐 Мову змінено на українську",
        'language_selection': "🌍 Оберіть мову:",
        'processing': "⏳ Обробляю ваш запит...",
        'error': "❌ Сталася помилка. Будь ласка, спробуйте пізніше.",
        'model_switched_gpt4': "🤖 Переключено на модель GPT-4",
        'model_switched_gemini': "✨ Переключено на модель Gemini",
        'model_switched_gpt4o': "🔮 Переключено на модель GPT-4O",
        'model_switched_gpt4o_mini': "🎯 Переключено на модель GPT-4O-mini",
        'model_switched_claude': "🎭 Переключено на модель Claude 3.5 Sonnet",
        'model_switched_claude_haiku': "🎋 Переключено на модель Claude 3.5 Haiku",
        'current_model': "Поточна модель: {model}",
        'safety_error': """⚠️ Я не можу обробити цей запит через правила безпеки.
Будь ласка, перефразуйте повідомлення."""
    }
}

__all__ = ['message_templates'] 