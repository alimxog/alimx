import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

# === توکن باتت رو اینجا بذار ===
BOT_TOKEN = "1234567890:ABCDefGhIJKlmNoPQRsTuvWXyZ"
ADMIN_ID = 123456789  # آیدی ادمین

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
pending_orders = {}

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("شماره مجازی", callback_data="virtual_number"))
    markup.add(InlineKeyboardButton("طراحی لوگو", callback_data="logo_design"))
    return markup

def pay_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("واریز کردم", callback_data="paid"))
    markup.add(InlineKeyboardButton("لغو", callback_data="cancel"))
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "به بات شاپینو خوش آومدی عسلم🫶😊", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    data = call.data

    if data == "virtual_number":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("امریکا 50 تومان", callback_data="virtual_usa_50"))
        bot.edit_message_text("دسته شماره مجازی:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "logo_design":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("طراحی ساده 100 تومان", callback_data="logo_simple_100"))
        bot.edit_message_text("دسته طراحی لوگو:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data in ["virtual_usa_50", "logo_simple_100"]:
        bot.edit_message_text("خوب ✅ حالا مبلغ را به کارت زیر واریز کن و دکمه 😊👌های زیر را بزن\n\n6219861990599986",
                              call.message.chat.id, call.message.message_id, reply_markup=pay_menu())

    elif data == "cancel":
        bot.edit_message_text("به منوی اصلی برگشتید.", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

    elif data == "paid":
        pending_orders[user_id] = call.message.text
        bot.send_message(ADMIN_ID, f"سفارش جدید از کاربر {user_id}\nآیا تایید می‌کنید؟",
                         reply_markup=InlineKeyboardMarkup([
                             [InlineKeyboardButton("تایید", callback_data="admin_accept")],
                             [InlineKeyboardButton("رد", callback_data="admin_reject")]
                         ]))
        bot.edit_message_text("سفارش شما ثبت شد، منتظر تایید ادمین باشید ✅",
                              call.message.chat.id, call.message.message_id)

    elif data == "admin_accept":
        for uid in pending_orders.keys():
            bot.send_message(uid, "سفارش شما توسط ادمین تایید شد ✅\n@PvAliMx")
        pending_orders.clear()
        bot.edit_message_text("سفارش تایید شد ✅", call.message.chat.id, call.message.message_id)

    elif data == "admin_reject":
        for uid in pending_orders.keys():
            bot.send_message(uid, "سفارش شما رد شد ❌")
        pending_orders.clear()
        bot.edit_message_text("سفارش رد شد ❌", call.message.chat.id, call.message.message_id)

# --- برای اتصال Render ---
@server.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}")
    return "Bot is ready!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
