
import telebot
import json
from datetime import datetime, timedelta

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# Загрузка базы подписчиков
try:
    with open("vip_users.json", "r") as f:
        vip_users = json.load(f)
except:
    vip_users = {}

# Сохраняем базу
def save_vip():
    with open("vip_users.json", "w") as f:
        json.dump(vip_users, f)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Добро пожаловать в P2P SCANNER BOT!\n\nДоступные команды:\n/курс — Актуальные цены\n/связки — Лучшие связки\n/калькулятор — Подсчёт прибыли\n/vip — VIP-связки\n/подписка — Условия подписки")

# Команда /подписка
@bot.message_handler(commands=['подписка'])
def subs(message):
    with open("subscription.txt", "r", encoding="utf-8") as f:
        sub_text = f.read()
    bot.send_message(message.chat.id, sub_text)

# Команда /активировать
@bot.message_handler(commands=['активировать'])
def activate(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите код (например, VIP-1, VIP-7, VIP-30):")
    bot.register_next_step_handler(msg, process_activation)

def process_activation(message):
    code = message.text.strip().upper()
    days = {"VIP-1": 1, "VIP-7": 7, "VIP-30": 30}
    if code in days:
        until = (datetime.now() + timedelta(days=days[code])).strftime("%Y-%m-%d")
        vip_users[str(message.chat.id)] = until
        save_vip()
        bot.send_message(message.chat.id, f"✅ VIP доступ активирован до {until}")
    else:
        bot.send_message(message.chat.id, "❌ Неверный код. Попробуйте снова.")

# Команда /vip
@bot.message_handler(commands=['vip'])
def vip(message):
    uid = str(message.chat.id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid in vip_users and vip_users[uid] >= today:
        bot.send_message(message.chat.id, "🔥 VIP-связки (пример):\n\n1. Купить на OKX за 1.00$ → продать на Binance за 1.05$\n2. Купить на Bybit за 1.01$ → продать на OKX за 1.06$\n📈 Прибыль до 5–6%")
    else:
        bot.send_message(message.chat.id, "🔒 У вас нет активной подписки. Введите /подписка чтобы оформить.")

bot.polling()
