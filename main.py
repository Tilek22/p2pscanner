
# 📦 Новый улучшенный main.py с оформлением, эмодзи и кнопками
import telebot
from telebot import types
import json
from datetime import datetime, timedelta

API_TOKEN = '8065004819:AAGCuaB5ImkIPHqQKp4alsX4ue9GFvpqt-4'
bot = telebot.TeleBot(API_TOKEN)

# Загрузка базы подписчиков
try:
    with open("vip_users.json", "r") as f:
        vip_users = json.load(f)
except:
    vip_users = {}

def save_vip():
    with open("vip_users.json", "w") as f:
        json.dump(vip_users, f)

# Главное меню с кнопками
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("📊 Курсы", "🔁 Связки")
main_menu.add("💎 Подписка", "👑 VIP")

# /start
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    bot.send_message(message.chat.id, f"👋 Привет, {name}!")
    bot.send_message(message.chat.id,
"Добро пожаловать в P2P SCANNER BOT 🔍\n\nВыбирай нужную функцию снизу:", reply_markup=main_menu)

# Кнопка "📊 Курсы"
@bot.message_handler(func=lambda msg: msg.text == "📊 Курсы")
def kurs(message):
    bot.send_message(message.chat.id, "💱 Актуальные курсы:\n\nUSDT/TON/TRX/BTC\n(данные обновляются...)")

# Кнопка "🔁 Связки"
@bot.message_handler(func=lambda msg: msg.text == "🔁 Связки")
def svyazki(message):
    text = "🔗 Топ 3 связки на сейчас:\n\n"
    text += "1️⃣ TON\n🔻 OKX → 1.20$\n🔺 Binance → 1.28$\n💰 Прибыль: +6.7%\n\n"
    text += "2️⃣ TRX\n🔻 Bybit → 0.267$\n🔺 OKX → 0.278$\n💰 Прибыль: +4.1%\n\n"
    text += "3️⃣ SHIB\n🔻 Bybit → 0.0000091$\n🔺 Binance → 0.0000097$\n💰 Прибыль: +6.6%"
    bot.send_message(message.chat.id, text)

# Кнопка "💎 Подписка"
@bot.message_handler(func=lambda msg: msg.text == "💎 Подписка")
@bot.message_handler(commands=['подписка'])
def subs(message):
    with open("subscription.txt", "r", encoding="utf-8") as f:
        sub_text = f.read()
    bot.send_message(message.chat.id, sub_text)

# Кнопка "👑 VIP"
@bot.message_handler(func=lambda msg: msg.text == "👑 VIP")
@bot.message_handler(commands=['vip'])
def vip(message):
    uid = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid in vip_users and vip_users[uid] >= today:
        bot.send_message(message.chat.id,
            "👑 VIP-связки:\n\nTON: OKX → 1.20$ → Binance → 1.28$ (+6.7%)\nTRX: Bybit → 0.267$ → OKX → 0.278$ (+4.1%)")
    else:
        bot.send_message(message.chat.id,
            "🔒 У вас нет активной подписки. Введите /подписка, чтобы оформить доступ.")

# /активировать
@bot.message_handler(commands=['активировать'])
def activate(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите код активации (VIP-1, VIP-7, VIP-30):")
    bot.register_next_step_handler(msg, process_activation)

def process_activation(message):
    code = message.text.strip().upper()
    days = {"VIP-1": 1, "VIP-7": 7, "VIP-30": 30}
    if code in days:
        until = (datetime.now() + timedelta(days=days[code])).strftime("%Y-%m-%d")
        vip_users[str(message.chat.id)] = until
        save_vip()
        bot.send_message(message.chat.id, f"✅ Подписка активирована до {until}")
    else:
        bot.send_message(message.chat.id, "❌ Неверный код. Попробуйте снова.")

bot.polling()
