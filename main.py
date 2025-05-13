# 📦 Обновлённый main.py с кнопкой «Мой ID» и автообновлением связок
import telebot
from telebot import types
import json
from datetime import datetime, timedelta
import threading
import time
from scanner import compare_all_exchanges

API_TOKEN = '8065004819:AAHsCVYP1dKWrZU8FGjSrd1UrOeBpcI5KZk'
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
main_menu.add("🔁 Связки", "👑 VIP")
main_menu.add("💎 Подписка", "📘 Помощь")
main_menu.add("👤 Мой ID")

# /start
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    logo = (
        "🔮 <b>P2P SCANNER BOT</b> 🔮\n"
        "<i>🔗 Автоматический поиск связок\n💸 Максимум прибыли — минимум риска</i>\n"
        "\nДобро пожаловать, <b>{}</b>!".format(name)
    )
    bot.send_message(message.chat.id, logo, reply_markup=main_menu, parse_mode="HTML")

# Кнопка "🔁 Связки"
@bot.message_handler(func=lambda msg: msg.text == "🔁 Связки")
@bot.message_handler(commands=['связки'])
def svyazki(message):
    text = "<b>🔗 Топ 3 связки (пример):</b>\n\n"
    text += "1️⃣ TON\n🔻 OKX → 1.20$\n🔺 Binance → 1.28$\n💰 Прибыль: +6.7%\n\n"
    text += "2️⃣ TRX\n🔻 Bybit → 0.267$\n🔺 OKX → 0.278$\n💰 Прибыль: +4.1%\n\n"
    text += "3️⃣ SHIB\n🔻 Bybit → 0.0000091$\n🔺 Binance → 0.0000097$\n💰 Прибыль: +6.6%\n\n💬 Поддержка: @La_Vistaa"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# Кнопка "💎 Подписка"
@bot.message_handler(func=lambda msg: msg.text == "💎 Подписка")
@bot.message_handler(commands=['подписка'])
def subs(message):
    sub_text = (
        "💎 <b>VIP ПОДПИСКА НА P2P СКАНЕР</b>:\n\n"
        "🔹 1 день — 500 KGS\n🔹 7 дней — 2 500 KGS\n🔹 30 дней — 7 500 KGS\n\n"
        "🔄 <i>Что ты получишь:</i>\n"
        "✅ Реальные P2P-связки\n✅ Автообновление\n✅ Binance, OKX, Bybit\n\n"
        "💳 <b>Оплата на карту:</b>\nVISA: <code>4021 8300 5087 1042</code>\nНа имя: А.Т\n\n"
        "📩 После оплаты отправьте скриншот или введите /активировать\n💬 Поддержка: @La_Vistaa"
    )
    bot.send_message(message.chat.id, sub_text, parse_mode="HTML")

# Кнопка "👑 VIP"
@bot.message_handler(func=lambda msg: msg.text == "👑 VIP")
@bot.message_handler(commands=['vip'])
def vip(message):
    uid = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid in vip_users and vip_users[uid] >= today:
        results = compare_all_exchanges()
        bot.send_message(message.chat.id, "\n".join(results))
    else:
        bot.send_message(message.chat.id,
            "🔒 У вас нет активной подписки. Введите /подписка, чтобы оформить доступ.", parse_mode="HTML")

# Кнопка "👤 Мой ID"
@bot.message_handler(func=lambda msg: msg.text == "👤 Мой ID")
@bot.message_handler(commands=['мой_профиль'])
def profile(message):
    uid = str(message.chat.id)
    user = message.from_user
    until = vip_users.get(uid, "нет")
    status = "✅ Активен до " + until if until != "нет" and until >= datetime.now().strftime("%Y-%m-%d") else "❌ Нет подписки"
    text = (
        f"👤 <b>Ваш профиль:</b>\n"
        f"Имя: {user.first_name}\n"
        f"ID: <code>{uid}</code>\n"
        f"Статус: {status}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# /помощь и кнопка 📘
@bot.message_handler(commands=['помощь'])
@bot.message_handler(func=lambda msg: msg.text == "📘 Помощь")
def help_command(message):
    help_text = (
        "📘 <b>Справка по командам:</b>\n\n"
        "/start — запуск бота\n"
        "/связки — 🔁 Пример связок\n"
        "/vip — 👑 Реальные связки\n"
        "/подписка — 💎 Условия\n"
        "/активировать — 🔐 Ввести код\n"
        "/мой_профиль — 👤 Ваш ID и статус\n"
        "/помощь — 📘 Меню помощи"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")

# Автонапоминание

def daily_vip_broadcast():
    while True:
        now = datetime.now()
        if now.hour in [10, 18] and now.minute == 0:
            today = now.strftime("%Y-%m-%d")
            for uid, expiry in vip_users.items():
                if expiry >= today:
                    bot.send_message(uid, "🧠 P2P BOT | v1.2\n\n💡 Проверь /vip — свежие связки между биржами")
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=daily_vip_broadcast, daemon=True).start()

bot.polling()
