import telebot
import sqlite3
import random
import time
import os
from telebot.types import *

# TOKENni Railway ENV dan oladi
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7543852010
ADMIN_USERNAME = "Fast_gamer_uz"

# ===== DATABASE =====
db = sqlite3.connect("bot.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
balance INTEGER,
preview INTEGER,
ref INTEGER,
last_task INTEGER
)
""")
db.commit()

# ===== KANALLAR =====
channels = [
    ("@Fast_gamer_mod","https://t.me/Fast_gamer_mod"),
    ("@Fast_prevyu","https://t.me/Fast_prevyu"),
    ("@FAST_MODS_BOT","https://t.me/FAST_MODS_BOT")
]

# ===== MENU =====
def menu(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💬 Vazifalar 💬")
    kb.add("⭐ AI yordamida Prevyu yasash ⭐")
    kb.add("💸 Pulga Prevyu buyurtma qilish 💸")
    kb.add("👥 Referal")

    if user_id == ADMIN_ID:
        kb.add("⚙️ Admin panel")

    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username

    args = msg.text.split()
    ref = 0

    if len(args) > 1:
        try:
            ref = int(args[1])
        except:
            pass

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (?,?,?,?,?,?)",
            (user_id, username, 0, 0, ref, 0)
        )
        db.commit()

        if ref != 0:
            cursor.execute("UPDATE users SET balance = balance + 10 WHERE id=?", (ref,))
            db.commit()

    inline = InlineKeyboardMarkup()
    inline.add(InlineKeyboardButton("➕ Guruhga qo‘shish ➕",
                                    url="https://t.me/Fast_prevyu_bot?startgroup=true"))

    bot.send_message(msg.chat.id, "Botga xush kelibsiz 👋", reply_markup=inline)
    bot.send_message(msg.chat.id, "👇 Menyu", reply_markup=menu(user_id))

# ===== VAZIFALAR =====
@bot.message_handler(func=lambda m: m.text == "💬 Vazifalar 💬")
def vazifa(msg):
    user_id = msg.from_user.id
    now = int(time.time())

    cursor.execute("SELECT last_task FROM users WHERE id=?", (user_id,))
    last = cursor.fetchone()[0]

    if now - last < 300:
        bot.send_message(msg.chat.id,
            "⏳ Iltimos 5-10 daqiqadan keyin yana urinib ko‘ring")
        return

    ch = random.choice(channels)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔒 Obuna bo‘lish", url=ch[1]))
    kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data=f"check|{ch[0]}"))

    bot.send_message(msg.chat.id,
        "📢 Kanalga obuna bo‘ling va 5 balans oling",
        reply_markup=kb)

    cursor.execute("UPDATE users SET last_task=? WHERE id=?", (now, user_id))
    db.commit()

# ===== TEKSHIRISH =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("check"))
def check(call):
    user_id = call.from_user.id
    channel = call.data.split("|")[1]

    try:
        status = bot.get_chat_member(channel, user_id).status
    except:
        status = "left"

    if status in ["member","administrator","creator"]:
        cursor.execute("UPDATE users SET balance = balance + 5 WHERE id=?", (user_id,))
        db.commit()

        bot.answer_callback_query(call.id, "✅ 5 balans qo‘shildi")
        bot.send_message(call.message.chat.id,
            "🎉 5 balans oldingiz!")
    else:
        bot.answer_callback_query(call.id, "❌ Avval obuna bo‘ling", show_alert=True)

# ===== REFERAL =====
@bot.message_handler(func=lambda m: m.text == "👥 Referal")
def referal(msg):
    link = f"https://t.me/{bot.get_me().username}?start={msg.from_user.id}"

    bot.send_message(msg.chat.id,
        f"👥 Referal linkingiz:\n{link}\n\nHar bir odam uchun 10 balans")

# ===== AI PREVIEW =====
@bot.message_handler(func=lambda m: m.text == "⭐ AI yordamida Prevyu yasash ⭐")
def ai(msg):
    cursor.execute("SELECT balance FROM users WHERE id=?", (msg.from_user.id,))
    balance = cursor.fetchone()[0]

    if balance < 100:
        bot.send_message(msg.chat.id, "❌ 100 balans kerak")
        return

    bot.send_message(msg.chat.id, "📸 Rasm yuboring")

# ===== RASM =====
@bot.message_handler(content_types=['photo'])
def photo(msg):
    images = [
        "https://i.imgur.com/9YQZ6Qp.jpeg",
        "https://i.imgur.com/7v5ASc8.jpeg",
        "https://i.imgur.com/k8FQK4F.jpeg"
    ]

    img = random.choice(images)

    bot.send_photo(msg.chat.id, img, caption="🔥 Prevyu tayyor!")

    cursor.execute(
        "UPDATE users SET balance = balance - 100, preview = preview + 1 WHERE id=?",
        (msg.from_user.id,)
    )
    db.commit()

# ===== BUYURTMA =====
@bot.message_handler(func=lambda m: m.text == "💸 Pulga Prevyu buyurtma qilish 💸")
def order(msg):
    bot.send_message(ADMIN_ID,
        f"💸 Yangi buyurtma\n@{msg.from_user.username}\nID: {msg.from_user.id}")

    bot.send_message(msg.chat.id, "✅ Adminga yuborildi")

# ===== ADMIN =====
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin panel")
def admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "⚙️ Admin panel ishlayapti")

# ===== RUN =====
print("Bot ishga tushdi")
bot.infinity_polling()
