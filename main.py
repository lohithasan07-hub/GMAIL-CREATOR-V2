import telebot
import random
import io
import time
from telebot import types

API_TOKEN = "8338478408:AAH1UbxlUs8s9ria4Xsfq3G2hDPwNtiDt5A"
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

user_data = {}

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
        types.InlineKeyboardButton("📨 Gmail GEN  [ 30 ]", callback_data="mode_30", style="success"),
        types.InlineKeyboardButton("📦 Gmail GEN  [ 10K ]", callback_data="mode_10k", style="success")
    )
    return markup

def get_gen_30_interface(chat_id):
    state = user_data.get(chat_id)
    if not state or not state.get('email_list'):
        return "❌ No Emails Found!", main_menu()
    
    current_idx = state['current_index']
    current_base = state['email_list'][current_idx]
    
    text = (
        f"<b>⚡ GMAIL GENERATOR ENGINE ⚡</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Target Account:</b>\n"
        f"<code>{current_base}</code>\n\n"
        f"📊 <b>Progress:</b> {current_idx + 1} / {len(state['email_list'])}\n"
        f"⚙️ <b>Status:</b> ACTIVE\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Select an action below:</i>"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Generate Button = Green
    markup.add(types.InlineKeyboardButton("⚙️ Generate Variant", callback_data="take_variant", style="success"))
    
    if len(state['email_list']) > 1:
        # Switch Button = Blue
        markup.add(types.InlineKeyboardButton("🔄 Switch Target Account", callback_data="switch_menu", style="primary"))
    
    # Main Menu Button = Red
    markup.add(types.InlineKeyboardButton("🌐 Main Menu", callback_data="back_to_main", style="danger"))
    
    return text, markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_data.pop(message.chat.id, None)
    welcome_text = (
        "<b>💥 EMAIL VARIANT 6.9 💥</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>Dev:</b> @Lohit_69\n"
        "🟢 <b>System:</b> ONLINE\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📥 <i>Select an operation mode:</i>"
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
        text = (
            "<b>📨 GMAIL GEN MODE [30]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <i>Send 1 to 10 Gmails (separated by space):</i>"
        )
        bot.edit_message_text(text, chat_id, call.message.message_id)
    
    elif call.data == "mode_10k":
        user_data[chat_id] = {'mode': '10k'}
        text = (
            "<b>📦 GMAIL GEN MODE [10K]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <i>Send 1 target Gmail. I will output a 10,000 variant file.</i>"
        )
        bot.edit_message_text(text, chat_id, call.message.message_id)

    elif call.data == "take_variant":
        if not state or state.get("busy"):
            bot.answer_callback_query(call.id, "⏳ Generating...", show_alert=False)
            return
        
        state["busy"] = True
        try:
            if state.get('last_msg_id'):
                try: bot.delete_message(chat_id, state['last_msg_id'])
                except: pass

            email_base = state['email_list'][state['current_index']]
            new_mail = generate_single_variant(email_base)
            
            bot.answer_callback_query(call.id, "✅ Variant Copied!")
            
            sent = bot.send_message(chat_id, f"<code>{new_mail}</code>")
            state['last_msg_id'] = sent.message_id
        finally:
            state["busy"] = False

    elif call.data == "switch_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, email in enumerate(state['email_list']):
            prefix = "► " if i == state['current_index'] else "  "
            markup.add(types.InlineKeyboardButton(f"{prefix}{email}", callback_data=f"set_idx_{i}"))
        
        markup.add(types.InlineKeyboardButton("🔙 Back to HUD", callback_data=f"set_idx_{state['current_index']}", style="danger"))
        
        text = (
            "<b>🔍 SELECT TARGET ACCOUNT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_idx_"):
        state['current_index'] = int(call.data.split("_")[2])
        text, markup = get_gen_30_interface(chat_id)
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id)
    
    if not state:
        bot.reply_to(message, "⚠️ <b>Select a mode first.</b> 👇", reply_markup=main_menu())
        return

    if state['mode'] == '30':
        emails = [e.strip() for e in message.text.split() if '@' in e][:10]
        if not emails: return
        
        state.update({'email_list': emails, 'current_index': 0, 'last_msg_id': None})
        
        text, markup = get_gen_30_interface(chat_id)
        bot.send_message(chat_id, text, reply_markup=markup)

    elif state['mode'] == '10k':
        wait_msg = bot.send_message(chat_id, "⏳ <b>Generating 10,000 Variants...</b>")
        variants = [generate_single_variant(message.text.strip()) for _ in range(10000)]
        file_buffer = io.BytesIO("\n".join(variants).encode('utf-8'))
        
        prefix = message.text.strip().split('@')[0]
        file_buffer.name = f"10K_{prefix}.txt"
        
        bot.delete_message(chat_id, wait_msg.message_id)
        bot.send_document(chat_id, file_buffer, caption="<b>✅ GENERATION COMPLETE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n🎯 Dev: @Lohit_69")

if __name__ == "__main__":
    print("System Online...")
    while True:
        try: bot.polling(none_stop=True)
        except: time.sleep(5)
