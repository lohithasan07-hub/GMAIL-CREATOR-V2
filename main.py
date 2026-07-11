import telebot
import random
from telebot import types

API_TOKEN = "8338478408:AAH1UbxlUs8s9ria4Xsfq3G2hDPwNtiDt5A"
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# ইন-মেমরি স্টোরেজ (সহজ রাখার জন্য, তবে ইউজার বাড়লে SQLite ব্যবহার করা ভালো)
user_data = {}

def generate_single_variant(email):
    local, domain = email.split("@")
    domain = domain.lower()
    # অন-দ্য-ফ্লাই লজিক: প্রি-জেনারেট না করে কল করার সময় জেনারেট করবে
    new_local = "".join(random.choice([c.lower(), c.upper()]) if c.isalpha() else c for c in local)
    return f"{new_local}@{domain}"

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 Gmail GEN - ⚡30 📨", callback_data="mode_30"),
        types.InlineKeyboardButton("📦 Gmail GEN - 10K 📦", callback_data="mode_10k"),
        types.InlineKeyboardButton("🔄 Reset/Unstuck", callback_data="reset_bot") # আনস্টাক বাটন
    )
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_data.pop(message.chat.id, None) # শুরুতেই ডাটা ক্লিয়ার
    welcome_text = "🎉 <b>EMAIL VARIANT 6.9 BOT ACTIVE</b> 🤖\n\n💥 <b>Created By</b> @Lohit_69💎"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    
    if call.data == "reset_bot":
        user_data.pop(chat_id, None)
        bot.answer_callback_query(call.id, "✅ Session Reset!")
        start_cmd(call.message)
        return

    # মোড হ্যান্ডলার এবং অন্যান্য লজিক আগের মতোই থাকবে, কিন্তু 
    # 'take_' লজিকে এখন generate_single_variant() কল করবে
    elif call.data.startswith("take_"):
        state = user_data.get(chat_id)
        if state and not state.get("busy"):
            state["busy"] = True
            try:
                # এখানে লিস্ট থেকে রিমুভ করার বদলে নতুন করে একটা জেনারেট করবে
                new_mail = generate_single_variant(state['email_list'][state['current_index']])
                bot.answer_callback_query(call.id, "✅ Copied!")
                bot.send_message(chat_id, f"<code>{new_mail}</code>")
            finally:
                state["busy"] = False
        bot.edit_message_text(call.message.text, chat_id, call.message.message_id, reply_markup=call.message.reply_markup)

    # বাকি মোড লজিক...
    elif call.data == "mode_30":
        user_data[chat_id] = {'mode': '30', 'email_list': [], 'current_index': 0}
        bot.edit_message_text("📨 <b>GMAIL GEN MODE (30)</b>\nজিমেইল পাঠান:", chat_id, call.message.message_id)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id)
    
    if state and state['mode'] == '30':
        state['email_list'] = [e.strip() for e in message.text.split() if '@' in e][:10]
        bot.send_message(chat_id, "✅ Gmails set! Use the menu to generate.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
