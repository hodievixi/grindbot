import telebot
from telebot import types
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Загрузка .env ===
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_JSON = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))

bot = telebot.TeleBot(TOKEN)

# === Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# === Главное меню ===
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('💳 Оплатить картой (30$)', '🪙 Оплатить криптой')
main_menu.row('📨 Поддержка')

# === Команда /start ===
@bot.message_handler(commands=['start'])
def start(message):
    photo = open('Frame 10.jpg', 'rb')
    bot.send_photo(
        message.chat.id,
        photo=photo,
        caption='👋 Добро пожаловать!\n\n🧠 Готов получить доступ к системе?\nВыбирай способ оплаты ниже:',
        reply_markup=main_menu
    )

# === Обработка текстов ===
@bot.message_handler(content_types=['text'])
def handle_message(message):
    username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"
    name = message.from_user.first_name
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    if message.text == '📨 Поддержка':
        bot.send_message(
            message.chat.id,
            "📨 Напиши нашему менеджеру: @grind_unversity\nОн поможет с оплатой и доступом."
        )

    elif message.text == '💳 Оплатить картой (30$)':
        bot.send_message(
            message.chat.id,
            "💳 Для оплаты картой — напиши сообщение:\n\n👉 *Хочу оплатить курс картой*\n\n🔗 @grind_unversity",
            parse_mode='Markdown'
        )
        sheet.append_row([name, username, now, "—", "💳 Карта"])

    elif message.text == '🪙 Оплатить криптой':
        bot.send_message(
            message.chat.id,
            "🪙 Отправь 25 USDT (TRC-20) на адрес:\n\n`TFfzrzShKw25V44BWHtewwXH12SLZvyDLg`\n\nПосле оплаты нажми кнопку ниже 👇",
            parse_mode='Markdown',
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Я оплатил", callback_data="paid_crypto")
            )
        )
    else:
        bot.send_message(message.chat.id, "Выбери способ оплаты ниже:", reply_markup=main_menu)

# === Обработка оплаты криптой ===
@bot.callback_query_handler(func=lambda call: call.data == "paid_crypto")
def confirm_crypto_payment(call):
    username = f"@{call.from_user.username}" if call.from_user.username else "нет юзернейма"
    name = call.from_user.first_name
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    sheet.append_row([name, username, now, "—", "🪙 Крипта"])
    bot.send_message(call.message.chat.id, "✅ Спасибо за оплату! Доступ скоро откроется.")
    bot.send_message(ADMIN_ID, f"💰 Оплата КРИПТОЙ от {username}")

# === Запуск ===
print("🚀 Бот запущен и ждёт жертв...")
bot.infinity_polling()
