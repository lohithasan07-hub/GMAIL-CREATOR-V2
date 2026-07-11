import telebot
import random
import io
import time
from telebot import types

API_TOKEN = "8338478408:AAH1UbxlUs8s9ria4Xsfq3G2hDPwNtiDt5A"
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

user_data = {}

# On-the-fly Generation (Memory Efficient)
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
        types.InlineKeyboardButton("📨 Gmail GEN - ⚡ 30", callback_data="mode_30"),
        types.InlineKeyboardButton("📦 Gmail GEN - ⚡ 10K", callback_data="mode_10k")
    )
    return markup

def get_gen_30_interface(chat_id):
    state = user_data.get(chat_id)
    if not state or not state.get('email_list'):
        return "❌ No Emails Found!", main_menu()
    
    current_idx = state['current_index']
    current_base = state['email_list'][current_idx]
    
    # 🌟 Professional HUD Layout
    text = (
        f"<blockquote>⚡ <b>GMAIL GENERATOR ENGINE</b>\n\n"
        f"📌 <b>Target Account:</b>\n"
        f"<code>{current_base}</code>\n\n"
        f"📊 <b>Progress:</b> {current_idx + 1}/{len(state['email_list'])}\n"
        f"⚙️ <b>Status:</b> Active\n\n"
        f"👇 <i>Select an action below:</i></blockquote>"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📧 Generate Variant", callback_data="take_variant"))
    
    if len(state['email_list']) > 1:
        markup.add(types.InlineKeyboardButton("🔄 Switch Gmail Account", callback_data="switch_menu"))
    
    markup.add(types.InlineKeyboardButton("🌐 Main Menu", callback_data="back_to_main"))
    
    return text, markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_data.pop(message.chat.id, None)
    welcome_text = (
        "<blockquote>🎉 <b>EMAIL VARIANT 6.9 BOT ACTIVE</b> 🤖\n\n"
        "💥 <b>Created By</b> @Lohit_69💎\n\n"
        "📥 <b>Select a mode to get started:</b></blockquote>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    state = user_data.get(chat_id)

    if call.data == "back_to_main":
        bot.delete_message(chat_id, call.message.message_id)
        start_cmd(call.message)
        return

    if call.data == "mode_30":
        user_data[chat_id] = {'mode': '30', 'email_list': []}
        bot.edit_message_text(
            "<blockquote>📨 <b>GMAIL GEN MODE (30)</b>\n\n"
            "📝 একসাথে ১–১০টি জিমেইল পাঠান (Space দিয়ে আলাদা করে):</blockquote>", 
            chat_id, call.message.message_id
        )
    
    elif call.data == "mode_10k":
        user_data[chat_id] = {'mode': '10k'}
        bot.edit_message_text(
            "<blockquote>📦 <b>GMAIL GEN 10K MODE</b>\n\n"
            "📝 যেকোনো ১টি জিমেইল পাঠান। আমি ১০,০০০ ভ্যারিয়েন্ট ফাইল করে দিচ্ছি।</blockquote>", 
            chat_id, call.message.message_id
        )

    elif call.data == "take_variant":
        if not state or state.get("busy"):
            bot.answer_callback_query(call.id, "⏳ Generating... Please wait.", show_alert=False)
            return
        
        state["busy"] = True
        try:
            if state.get('last_msg_id'):
                try: bot.delete_message(chat_id, state['last_msg_id'])
                except: pass

            email_base = state['email_list'][state['current_index']]
            new_mail = generate_single_variant(email_base)
            
            bot.answer_callback_query(call.id, "✅ Variant Copied to Chat!")
            
            sent = bot.send_message(chat_id, f"<code>{new_mail}</code>")
            state['last_msg_id'] = sent.message_id
        finally:
            state["busy"] = False

    elif call.data == "switch_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, email in enumerate(state['email_list']):
            prefix = "🟢 " if i == state['current_index'] else "⚪ "
            markup.add(types.InlineKeyboardButton(f"{prefix}{email}", callback_data=f"set_idx_{i}"))
        
        markup.add(types.InlineKeyboardButton("🔙 Back to HUD", callback_data=f"set_idx_{state['current_index']}"))
        bot.edit_message_text("<blockquote>🔍 <b>Select Account:</b></blockquote>", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_idx_"):
        state['current_index'] = int(call.data.split("_")[2])
        text, markup = get_gen_30_interface(chat_id)
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id)
    
    if not state:
        bot.reply_to(message, "⚠️ <b>আগে মোড সিলেক্ট করুন</b> 👇", reply_markup=main_menu())
        return

    if state['mode'] == '30':
        emails = [e.strip() for e in message.text.split() if '@' in e][:10]
        if not emails: return
        
        state.update({'email_list': emails, 'current_index': 0, 'last_msg_id': None})
        
        # User message deletion removed! Your sent Gmails will stay visible.

        text, markup = get_gen_30_interface(chat_id)
        bot.send_message(chat_id, text, reply_markup=markup)

    elif state['mode'] == '10k':
        wait_msg = bot.send_message(chat_id, "⏳ <b>Generating 10,000 Variants...</b>")
        variants = [generate_single_variant(message.text.strip()) for _ in range(10000)]
        file_buffer = io.BytesIO("\n".join(variants).encode('utf-8'))
        file_buffer.name = f"10K_{message.text.strip().split('@')[0]}.txt"
        
        bot.delete_message(chat_id, wait_msg.message_id)
        bot.send_document(chat_id, file_buffer, caption="✅ <b>Generation Complete!</b>\n🎯 By @Lohit_69")

if __name__ == "__main__":
    print("Bot is running...")
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)
