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

# === Google Sheets подключение ===
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# === Главное меню ===
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row('📚 О курсе', '💰 Стоимость')
main_menu.row('🛒 Купить курс', '📨 Поддержка')

# === Инлайн-кнопки с UTM-параметрами ===
def get_payment_markup():
    card_payload = "card"
    crypto_payload = "crypto"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 Оплатить картой (30$)", url=f"https://t.me/grind_unversity?start={card_payload}"),
        types.InlineKeyboardButton("🪙 Оплатить криптой (25$)", url=f"https://t.me/grind_unversity?start={crypto_payload}")
    )
    return markup

# === Опросник ===
def ask_user_info(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('✅ Да', '❌ Нет')
    bot.send_message(chat_id, 'Ты уже работал в сфере диджитал или только начинаешь?', reply_markup=markup)

# === Обработка команды /start ===
@bot.message_handler(commands=['start'])
def start(message):
    payload = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

    # Если в start передан способ оплаты
    if payload in ['card', 'crypto']:
        payment = "💳 Карта" if payload == "card" else "🪙 Крипта"
        # Найти пользователя по username и обновить способ оплаты
        records = sheet.get_all_records()
        for i, row in enumerate(records, start=2):  # начиная со второй строки
            if row['Username'] == username:
                sheet.update_cell(i, 5, payment)
                bot.send_message(message.chat.id, f"✅ Спасибо! Зафиксировал способ оплаты: {payment}")
                return

    # Обычный старт
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в Grind University ⚡️\nЗдесь ты найдешь путь к цифровой профессии и заработку.',
        reply_markup=main_menu
    )
    ask_user_info(message.chat.id)

# === Тексты ===
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
            bot.send_message(message.chat.id, "Ошибка: файл 'Frame 10.jpg' не найден.")

    elif message.text == '💰 Стоимость':
        bot.send_message(
            message.chat.id,
            '💵 Стоимость курса:\n▫️ 30$ — при оплате картой\n▫️ 25$ — при оплате криптой\n\n📌 Оплата напрямую в боте или через менеджера.'
        )

    elif message.text == '🛒 Купить курс':
        bot.send_message(
            message.chat.id,
            'Выбери способ оплаты ниже, и ты получишь инструкции от менеджера:',
            reply_markup=get_payment_markup()
        )

    elif message.text == '📨 Поддержка':
        bot.send_message(
            message.chat.id,
            '❓ Есть вопросы? Напиши менеджеру: @grind_unversity\n📌 Он поможет с оплатой, доступом и бонусами.'
        )

    elif message.text in ['✅ Да', '❌ Нет']:
        answer = 'опыт есть' if message.text == '✅ Да' else 'опыта нет'
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

        row = [message.from_user.first_name, username, timestamp, answer, '—']
        sheet.append_row(row)

        bot.send_message(ADMIN_ID, f"🧾 Новый пользователь:\nИмя: {message.from_user.first_name}\nЮзер: {username}\nОпыт: {answer}")
        bot.send_message(message.chat.id, "Спасибо! Выбирай действие из меню 👇", reply_markup=main_menu)

    else:
        bot.send_message(
            message.chat.id,
            'Я не понял команду 😅\nВыбери вариант из меню ниже:',
            reply_markup=main_menu
        )

# === Запуск ===
print("🤖 Бот запущен и готов к работе")
bot.infinity_polling()
