import telebot
from telebot import types
import urllib.parse
import os
import json
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === Загрузка переменных окружения ===
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS")

bot = telebot.TeleBot(TOKEN)

# === Настройка Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# === Главное меню ===
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('💳 Оплатить картой (30$)', '🪙 Оплатить криптой')
main_menu.row('📨 Поддержка')

# === Команда /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в Grind University ⚡️\nЗдесь ты найдешь путь к цифровой профессии и заработку.',
        reply_markup=main_menu
    )

# === Обработка текстов ===
@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == '📨 Поддержка':
        bot.send_message(
            message.chat.id,
            '❓ Есть вопросы? Напиши менеджеру: @grind_unversity\n📌 Он поможет с оплатой, доступом и бонусами.'
        )

    elif message.text == '💳 Оплатить картой (30$)':
        bot.send_message(
            message.chat.id,
            "💳 Для оплаты картой напиши:\n@grind_unversity\nСообщение: *Хочу оплатить курс картой*",
            parse_mode='Markdown'
        )
        sheet.append_row([
            message.from_user.first_name,
            f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма",
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            "—",
            "💳 Карта"
        ])

    elif message.text == '🪙 Оплатить криптой':
        bot.send_message(
            message.chat.id,
            "🔗 Отправь 25 USDT (TRC-20) на адрес:\n\n`TUxCoiYX3kzBXP7Uxv3ziuyBZwrpYbcxZP`\n\nПосле оплаты нажми кнопку ниже 👇",
            parse_mode='Markdown',
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Я оплатил", callback_data="paid_crypto")
            )
        )

    else:
        bot.send_message(
            message.chat.id,
            'Выбери способ оплаты ниже или обратись в поддержку:',
            reply_markup=main_menu
        )

# === Обработка кнопки "Я оплатил" ===
@bot.callback_query_handler(func=lambda call: call.data == "paid_crypto")
def confirm_crypto_payment(call):
    username = f"@{call.from_user.username}" if call.from_user.username else "нет юзернейма"
    sheet.append_row([
        call.from_user.first_name,
        username,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        "—",
        "🪙 Крипта"
    ])
    bot.send_message(call.message.chat.id, "Спасибо за оплату! 🔓 Доступ откроется в ближайшее время.")
    bot.send_message(ADMIN_ID, f"💰 Оплата КРИПТОЙ от {username}")

# === Запуск ===
print('🤖 Бот работает и ждёт клиентов...')
bot.infinity_polling()
