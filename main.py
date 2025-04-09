import telebot
from telebot import types
import urllib.parse
import os
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
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# === Главное меню ===
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('📚 О курсе', '💰 Стоимость')
main_menu.row('🛒 Купить курс', '📨 Поддержка')

# === Кнопки оплаты ===
def get_payment_markup():
    card_message = urllib.parse.quote("Хочу оплатить курс картой")
    url = f"https://t.me/grind_unversity?start={card_message}"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 Оплатить картой (30$)", url=url),
        types.InlineKeyboardButton("🪙 Оплатить криптой (25$)", callback_data="pay_crypto")
    )
    return markup

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в Grind University ⚡️\nЗдесь ты найдешь путь к цифровой профессии и заработку.',
        reply_markup=main_menu
    )

# === Обработка сообщений ===
@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == '📚 О курсе':
        try:
            with open('Frame 10.jpg', 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption='📦 В курсе: 16+ модулей по маркетингу, YouTube, Telegram, SEO и многому другому.\n\n🎓 Всё чётко по папкам: видео, таблицы, гайды и эфиры.'
                )
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Ошибка: нет файла Frame 10.jpg рядом с ботом.")

    elif message.text == '💰 Стоимость':
        bot.send_message(
            message.chat.id,
            '💵 Стоимость курса:\n▫️ 30$ — при оплате картой\n▫️ 25$ — при оплате криптой\n\n📌 Нажми «Купить курс» чтобы выбрать способ.'
        )

    elif message.text == '🛒 Купить курс':
        bot.send_message(
            message.chat.id,
            '👇 Выбери способ оплаты:',
            reply_markup=get_payment_markup()
        )

    elif message.text == '📨 Поддержка':
        bot.send_message(
            message.chat.id,
            '❓ Вопросы? Пиши менеджеру: @grind_unversity'
        )

# === Обработка кнопки "Оплатить криптой" ===
@bot.callback_query_handler(func=lambda call: call.data == "pay_crypto")
def crypto_payment(call):
    username = f"@{call.from_user.username}" if call.from_user.username else "нет юзернейма"
    bot.send_message(
        call.message.chat.id,
        "🪙 Отправь **25 USDT (TRC-20)** на кошелек:\n`TFfzrzShKw25V44BWHtewwXH12SLZvyDLg`\n\nПосле оплаты нажми кнопку ниже.",
        parse_mode='Markdown',
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Я оплатил", callback_data="paid_crypto")
        )
    )

# === Подтверждение крипто-оплаты ===
@bot.callback_query_handler(func=lambda call: call.data == "paid_crypto")
def confirm_crypto(call):
    username = f"@{call.from_user.username}" if call.from_user.username else "нет юзернейма"
    sheet.append_row([
        call.from_user.first_name,
        username,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        "—",
        "🪙 Крипта"
    ])
    bot.send_message(call.message.chat.id, "✅ Спасибо за оплату! Доступ будет выдан вручную в ближайшее время.")
    bot.send_message(ADMIN_ID, f"💰 Оплата криптой от {username}")

# === Запуск ===
print("🤖 Бот работает. Спи спокойно, солдат цифрового фронта.")
bot.infinity_polling()
