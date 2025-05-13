# 📦 main.py с админ-командой /добавить_vip, /статистика и автоочисткой
import telebot
from telebot import types
import json
from datetime import datetime, timedelta
import threading
import time
from scanner import compare_all_exchanges

API_TOKEN = '8065004819:AAHsCVYP1dKWrZU8FGjSrd1UrOeBpcI5KZk'
ADMIN_ID = 7833365313
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

# Очистка просроченных подписок
def clean_expired_vips():
    today = datetime.now().strftime("%Y-%m-%d")
    expired = [uid for uid, date in vip_users.items() if date < today]
    for uid in expired:
        del vip_users[uid]
    if expired:
        save_vip()

clean_expired_vips()

# Главное меню с кнопками
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("🔁 Связки", "👑 VIP")
main_menu.add("💎 Подписка", "📘 Помощь")
main_menu.add("👤 Мой ID")

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    logo = (
        "🔮 <b>P2P SCANNER BOT</b> 🔮\n"
        "<i>🔗 Автоматический поиск связок\n💸 Максимум прибыли — минимум риска</i>\n"
        f"\nДобро пожаловать, <b>{name}</b>!"
    )
    bot.send_message(message.chat.id, logo, reply_markup=main_menu, parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "🔁 Связки")
@bot.message_handler(commands=['связки'])
def svyazki(message):
    text = "<b>🔗 Топ 3 связки (пример):</b>\n\n"
    text += "1️⃣ TON\n🔻 OKX → 1.20$\n🔺 Binance → 1.28$\n💰 Прибыль: +6.7%\n\n"
    text += "2️⃣ TRX\n🔻 Bybit → 0.267$\n🔺 OKX → 0.278$\n💰 Прибыль: +4.1%\n\n"
    text += "3️⃣ SHIB\n🔻 Bybit → 0.0000091$\n🔺 Binance → 0.0000097$\n💰 Прибыль: +6.6%\n\n💬 Поддержка: @La_Vistaa"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

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

@bot.message_handler(func=lambda msg: msg.text == "👑 VIP")
@bot.message_handler(commands=['vip'])
def vip(message):
    uid = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid in vip_users and vip_users[uid] >= today:
        results = compare_all_exchanges()
        bot.send_message(message.chat.id, "\n".join(results))
    else:
        bot.send_message(message.chat.id, "🔒 У вас нет активной подписки. Введите /подписка", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "👤 Мой ID")
@bot.message_handler(commands=['мой_профиль'])
def profile(message):
    uid = str(message.chat.id)
    user = message.from_user
    until = vip_users.get(uid, "нет")
    status = "✅ Активен до " + until if until != "нет" and until >= datetime.now().strftime("%Y-%m-%d") else "❌ Нет подписки"
    text = (
        f"👤 <b>Ваш профиль:</b>\nИмя: {user.first_name}\nID: <code>{uid}</code>\nСтатус: {status}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['добавить_vip'])
def add_vip(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        uid = parts[1]
        days = int(parts[2])
        until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        vip_users[uid] = until
        save_vip()
        bot.send_message(message.chat.id, f"✅ Пользователь {uid} получил VIP до {until}")
    except:
        bot.send_message(message.chat.id, "⚠️ Формат: /добавить_vip chat_id дни")

@bot.message_handler(commands=['статистика'])
def stats(message):
    total = len(vip_users)
    today = datetime.now().strftime("%Y-%m-%d")
    active = sum(1 for d in vip_users.values() if d >= today)
    text = f"📊 VIP статистика:\nВсего: {total}\nАктивных: {active}"
    if message.chat.id == ADMIN_ID:
        ids = "\n".join(vip_users.keys())
        text += f"\n\n🧾 Все ID:\n{ids}"
    bot.send_message(message.chat.id, text)

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
        "/добавить_vip — 🛠️ (только админ)\n"
        "/статистика — 📊 VIP-аналитика"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")

# Автонапоминание

def daily_vip_broadcast():
    while True:
        now = datetime.now()
        if now.hour in [10, 18] and now.minute == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            for uid, expiry in vip_users.items():
                if expiry >= today:
                    bot.send_message(uid, "🧠 P2P BOT | v1.2\n\n💡 Проверь /vip — свежие связки между биржами")
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=daily_vip_broadcast, daemon=True).start()

bot.polling()
