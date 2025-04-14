import telebot
from telebot import types
import os
from dotenv import load_dotenv

# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
print(f"BOT TOKEN IS: {repr(TOKEN)}")


# === Главное меню ===
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row("🧠 О курсе", "💸 Стоимость")
main_menu.row("📋 FAQ", "🧑‍💻 Менеджер")

# === /start ===
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Grind University ⚡️\n\nПознакомься с курсом и напиши, если будут вопросы:",
        reply_markup=main_menu
    )

# === Обработка сообщений ===
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "🧠 О курсе":
        bot.send_message(
            message.chat.id,
            "📦 Внутри курса:\n\n— YouTube / Telegram / TikTok / SEO / Freelance / Продажи\n— 16+ структурированных модулей\n— Таблицы, скрипты, гайды, эфиры\n— Бонусы и апдейты"
        )

    elif message.text == "💸 Стоимость":
        bot.send_message(
            message.chat.id,
            "💰 Цена курса:\n▫️ 30$ — оплата картой\n▫️ 25$ — оплата криптой\n\n⚠️ Оплата только через менеджера."

        )

    elif message.text == "📋 FAQ":
        bot.send_message(
            message.chat.id,
            "❓ Частые вопросы:\n\n— Курс даётся навсегда?\nДа, доступ бессрочный.\n\n— Есть ли поддержка?\nДа, куратор.\n\n— Можно начать с нуля?\nДа, всё объясняется пошагово."

        )

    elif message.text == "🧑‍💻 Менеджер":
        bot.send_message(
            message.chat.id,
            "📩 Напиши менеджеру: @grind_unversity\n\nОн ответит на любые вопросы и поможет с оплатой."
        )

    else:
        bot.send_message(message.chat.id, "Выбери вариант из меню 👇", reply_markup=main_menu)

# === Старт бота ===
print("🤖 Бот ознакомительный режим активен")
bot.infinity_polling()
