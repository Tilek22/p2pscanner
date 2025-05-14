# 📦 Финальный main.py для P2P SCANNER бота
import telebot
from telebot import types
import json
from datetime import datetime, timedelta
from scanner import compare_all_exchanges
from fpdf import FPDF

API_TOKEN = '8065004819:AAFP4n-1CteYJkl8mG6DscN_kHqcySD8QGk'
ADMIN_ID = 7833365313
bot = telebot.TeleBot(API_TOKEN)

# Загрузка и сохранение VIP пользователей
try:
    with open("vip_users.json", "r") as f:
        vip_users = json.load(f)
except:
    vip_users = {}

def save_vip():
    with open("vip_users.json", "w") as f:
        json.dump(vip_users, f)

def clean_expired_vips():
    today = datetime.now().strftime("%Y-%m-%d")
    expired = [uid for uid, date in vip_users.items() if date < today]
    for uid in expired:
        del vip_users[uid]
    if expired:
        save_vip()
clean_expired_vips()

# Главное меню
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🔁 Связки", "👑 VIP")
main_menu.add("📈 Калькулятор", "📘 Помощь")
main_menu.add("💎 Подписка", "👤 Мой ID")

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    bot.send_message(message.chat.id, f"🔮 <b>P2P SCANNER BOT</b>\nДобро пожаловать, <b>{name}</b>!",
                     parse_mode="HTML", reply_markup=main_menu)

# Псевдо-связки
@bot.message_handler(func=lambda msg: msg.text == "🔁 Связки")
@bot.message_handler(commands=['связки'])
def svyazki(message):
    bot.send_message(message.chat.id, "🧠 Это демо. Чтобы видеть актуальные связки, используйте /vip")

# Подписка
@bot.message_handler(func=lambda msg: msg.text == "💎 Подписка")
@bot.message_handler(commands=['подписка'])
def subs(message):
    text = (
        "💎 <b>VIP Подписка:</b>\n\n"
        "🔹 1 день — 500 KGS\n🔹 7 дней — 2500 KGS\n🔹 30 дней — 7500 KGS\n\n"
        "💳 Оплата на VISA: <code>4021 8300 5087 1042</code>\n"
        "После оплаты введите /активировать\n\n"
        "🤖 Бот: @P2p_sng_bot"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# Команда VIP
@bot.message_handler(func=lambda msg: msg.text == "👑 VIP")
@bot.message_handler(commands=['vip'])
def vip(message):
    uid = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid in vip_users and vip_users[uid] >= today:
        results = compare_all_exchanges()
        bot.send_message(message.chat.id, "\n".join(results))
    else:
        bot.send_message(message.chat.id, "🔒 Нет подписки. Используйте /подписка", parse_mode="HTML")

# Мой ID
@bot.message_handler(func=lambda msg: msg.text == "👤 Мой ID")
@bot.message_handler(commands=['мой_профиль'])
def profile(message):
    uid = str(message.chat.id)
    name = message.from_user.first_name
    until = vip_users.get(uid, "нет")
    status = "✅ До " + until if until >= datetime.now().strftime("%Y-%m-%d") else "❌ Нет подписки"
    text = f"👤 <b>{name}</b>\nID: <code>{uid}</code>\nСтатус: {status}"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# Калькулятор сложного процента
@bot.message_handler(func=lambda msg: msg.text == "📈 Калькулятор")
@bot.message_handler(commands=['калькулятор'])
def start_calc(message):
    msg = bot.send_message(message.chat.id, "📊 Введите дневной % доходности (например: 1.5):")
    bot.register_next_step_handler(msg, process_percent)

def process_percent(message):
    try:
        percent = float(message.text.strip())
        msg = bot.send_message(message.chat.id, "📆 На сколько дней рассчитать?")
        bot.register_next_step_handler(msg, lambda m: process_days(m, percent))
    except:
        bot.send_message(message.chat.id, "❌ Введите число, например 1.5")

def process_days(message, percent):
    try:
        days = int(message.text.strip())
        start = 1000
        final = start * (1 + percent / 100) ** days
        bot.send_message(message.chat.id,
                         f"📈 Начальная сумма: $1000\n📉 Дневной %: {percent}%\n📆 Дней: {days}\n\n💰 Итог: <b>${final:.2f}</b>",
                         parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Введите целое число дней")

# Обязательно запускаем бота
bot.polling(none_stop=True)
