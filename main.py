# ⚙️ Финальный main.py с PDF, админкой, /отчёт, автоочисткой и всем нужным
import telebot
from telebot import types
import json
from datetime import datetime, timedelta
import threading
import time
from scanner import compare_all_exchanges
from fpdf import FPDF

API_TOKEN = '8065004819:AAHsCVYP1dKWrZU8FGjSrd1UrOeBpcI5KZk'
ADMIN_ID = 7833365313
bot = telebot.TeleBot(API_TOKEN)

# Загрузка базы
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
main_menu.add("💎 Подписка", "📘 Помощь")
main_menu.add("👤 Мой ID")

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    bot.send_message(message.chat.id,
        f"🔮 <b>P2P SCANNER BOT</b>\nДобро пожаловать, <b>{name}</b>!",
        parse_mode="HTML", reply_markup=main_menu)

@bot.message_handler(func=lambda msg: msg.text == "🔁 Связки")
@bot.message_handler(commands=['связки'])
def svyazki(message):
    bot.send_message(message.chat.id,
        "🧠 Это демо. Чтобы видеть актуальные связки, используйте /vip")

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
            "🔒 Нет подписки. Используйте /подписка", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "👤 Мой ID")
@bot.message_handler(commands=['мой_профиль'])
def profile(message):
    uid = str(message.chat.id)
    name = message.from_user.first_name
    until = vip_users.get(uid, "нет")
    status = "✅ До " + until if until >= datetime.now().strftime("%Y-%m-%d") else "❌ Нет подписки"
    text = f"👤 <b>{name}</b>\nID: <code>{uid}</code>\nСтатус: {status}"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['активировать'])
def activate(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите код (VIP-1, VIP-7, VIP-30):")
    bot.register_next_step_handler(msg, process_code)

def process_code(message):
    code = message.text.strip().upper()
    days_map = {"VIP-1": 1, "VIP-7": 7, "VIP-30": 30}
    if code in days_map:
        uid = str(message.chat.id)
        until = (datetime.now() + timedelta(days=days_map[code])).strftime("%Y-%m-%d")
        vip_users[uid] = until
        save_vip()
        bot.send_message(message.chat.id, f"✅ Подписка активна до {until}")
    else:
        bot.send_message(message.chat.id, "❌ Неверный код")

# PDF генерация
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "P2P Profit Report", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True, align="C")
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Telegram bot: @P2p_sng_bot", 0, 0, "C")
    def chapter(self, title, body):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)

@bot.message_handler(commands=['отчёт'])
def report(message):
    uid = str(message.chat.id)
    if uid not in vip_users or vip_users[uid] < datetime.now().strftime("%Y-%m-%d"):
        bot.send_message(message.chat.id, "❌ Только для VIP")
        return
    results = compare_all_exchanges()
    clean = [r.replace("→", ">").replace("%", "").replace("💰", "Profit:") for r in results]
    pdf = PDF()
    pdf.add_page()
    pdf.chapter("Top Arbitrage Opportunities:", "\n\n".join(clean))
    path = f"report_{uid}.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        bot.send_document(message.chat.id, f, visible_file_name="P2P_SCANNER_Report.pdf")

# Админ-функции
@bot.message_handler(commands=['добавить_vip'])
def addvip(message):
    if message.chat.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        uid, days = parts[1], int(parts[2])
        until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        vip_users[uid] = until
        save_vip()
        bot.send_message(message.chat.id, f"✅ {uid} → VIP до {until}")
    except:
        bot.send_message(message.chat.id, "Формат: /добавить_vip chat_id дни")

@bot.message_handler(commands=['статистика'])
def stats(message):
    total = len(vip_users)
    today = datetime.now().strftime("%Y-%m-%d")
    active = sum(1 for d in vip_users.values() if d >= today)
    bot.send_message(message.chat.id,
        f"📊 Всего VIP: {total}\nАктивных: {active}")

@bot.message_handler(commands=['помощь'])
@bot.message_handler(func=lambda msg: msg.text == "📘 Помощь")
def helpmsg(message):
    text = (
        "/start — запуск\n/vip — связки\n/мой_профиль — статус\n/отчёт — PDF\n/подписка — как оплатить\n/активировать — ввести код\n/добавить_vip — вручную\n/статистика — список VIP")
    bot.send_message(message.chat.id, text)

# Автопинг

def auto_vip_ping():
    while True:
        now = datetime.now()
        if now.hour in [10, 18] and now.minute == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            for uid, date in vip_users.items():
                if date >= today:
                    bot.send_message(uid, "🔔 Проверь /vip — новые P2P-связки")
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=auto_vip_ping, daemon=True).start()

bot.polling()
