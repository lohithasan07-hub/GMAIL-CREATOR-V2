import telebot
import random
import io
import time
from telebot import types

API_TOKEN = "8338478408:AAH1UbxlUs8s9ria4Xsfq3G2hDPwNtiDt5A"
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

user_data = {}

# অন-দ্য-ফ্লাই জেনারেশন ফাংশন (মেমরি সাশ্রয়ী)
def generate_single_variant(email):
    try:
        local, domain = email.split("@")
        domain = domain.lower()
        new_local = "".join(random.choice([c.lower(), c.upper()]) if c.isalpha() else c for c in local)
        return f"{new_local}@{domain}"
    except: return email

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 Gmail GEN - ⚡30 📨", callback_data="mode_30"),
        types.InlineKeyboardButton("📦 Gmail GEN - ⚡ 10K 📦", callback_data="mode_10k"),
        types.InlineKeyboardButton("🔄 Reset/Unstuck", callback_data="reset_bot")
    )
    return markup

def get_gen_30_interface(chat_id):
    state = user_data.get(chat_id)
    if not state or not state.get('email_list'):
        return "❌ No Emails Found!", main_menu()
    
    current_idx = state['current_index']
    current_base = state['email_list'][current_idx]
    
    text = (
        f"⚡ <b>GMAIL GENERATOR (On-The-Fly)</b>\n\n"
        f"📌 <b>Current:</b> <code>{current_base}</code>\n"
        f"📊 <b>Progress:</b> {current_idx + 1}/{len(state['email_list'])}\n\n"
        f"👇 <i>Click to generate a variant</i>"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📧 Generate Variant", callback_data="take_variant"))
    
    controls = []
    if len(state['email_list']) > 1:
        controls.append(types.InlineKeyboardButton("🔄 Switch Gmail", callback_data="switch_menu"))
    
    controls.append(types.InlineKeyboardButton("🔝 Main Menu", callback_data="back_to_main"))
    markup.add(*controls)
    return text, markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_data.pop(message.chat.id, None)
    welcome_text = ("🎉 <b>EMAIL VARIANT 6.9 BOT ACTIVE</b> 🤖\n\n"
                    "💥 <b>Created By</b> @Lohit_69💎\n\n"
                    "📥 <b>SEND AN EMAIL ADDRESS:</b>")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    state = user_data.get(chat_id)

    if call.data == "reset_bot":
        user_data.pop(chat_id, None)
        bot.answer_callback_query(call.id, "✅ Session Reset!")
        start_cmd(call.message)
        return

    if call.data == "mode_30":
        user_data[chat_id] = {'mode': '30', 'email_list': []}
        bot.edit_message_text("📨 <b>GMAIL GEN MODE (30)</b>\n\n১০টি জিমেইল পাঠান:", chat_id, call.message.message_id)
    
    elif call.data == "mode_10k":
        user_data[chat_id] = {'mode': '10k'}
        bot.edit_message_text("📦 <b>GMAIL GEN 10K MODE</b>\n\n১টি জিমেইল পাঠান।", chat_id, call.message.message_id)

    elif call.data == "take_variant":
        if not state or state.get("busy"):
            bot.answer_callback_query(call.id, "⏳ Please wait...", show_alert=True)
            return
        
        state["busy"] = True
        try:
            email_base = state['email_list'][state['current_index']]
            new_mail = generate_single_variant(email_base)
            bot.answer_callback_query(call.id, "✅ Generated!")
            bot.send_message(chat_id, f"<code>{new_mail}</code>")
        finally:
            state["busy"] = False

    elif call.data == "switch_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, email in enumerate(state['email_list']):
            markup.add(types.InlineKeyboardButton(f"{'📍 ' if i == state['current_index'] else ''}{email}", callback_data=f"set_idx_{i}"))
        bot.edit_message_text("🔍 Select:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_idx_"):
        state['current_index'] = int(call.data.split("_")[2])
        text, markup = get_gen_30_interface(chat_id)
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id)
    
    if not state:
        bot.reply_to(message, "আগে মোড সিলেক্ট করুন 👇", reply_markup=main_menu())
        return

    if state['mode'] == '30':
        emails = [e.strip() for e in message.text.split() if '@' in e][:10]
        if not emails: return
        state.update({'email_list': emails, 'current_index': 0})
        text, markup = get_gen_30_interface(chat_id)
        bot.send_message(chat_id, text, reply_markup=markup)

    elif state['mode'] == '10k':
        bot.send_message(chat_id, "⏳ Generating...")
        variants = [generate_single_variant(message.text.strip()) for _ in range(10000)]
        file_buffer = io.BytesIO("\n".join(variants).encode('utf-8'))
        file_buffer.name = "10k_variants.txt"
        bot.send_document(chat_id, file_buffer)

if __name__ == "__main__":
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)
