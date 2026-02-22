import telebot
import random
import io
import os
import time
from telebot import types

API_TOKEN = os.getenv("BOT_TOKEN", "8338478408:AAEV3otptv8Udec344Pnj3n_57exdMy1KwU")
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

user_data = {}

def generate_variants(email, count):
    try:
        local, domain = email.split("@")
        domain = domain.lower()
        results = set()
        max_attempts = count * 10
        attempts = 0
        while len(results) < count and attempts < max_attempts:
            attempts += 1
            new_local = "".join(random.choice([c.lower(), c.upper()]) if c.isalpha() else c for c in local)
            results.add(f"{new_local}@{domain}")
        return list(results)
    except: return []

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 Gmail GEN - ⚡30 📨", callback_data="mode_30"),
        types.InlineKeyboardButton("📦 Gmail GEN - ⚡ 10K 📦", callback_data="mode_10k")
    )
    return markup

def get_gen_30_interface(chat_id):
    state = user_data.get(chat_id)
    if not state or not state['email_list']:
        return "❌ No Emails Found!", None
    
    current_idx = state['current_index']
    current_base = state['email_list'][current_idx]
    variants = state['variants_dict'][current_base]
    
    if not variants:
        # যদি এই জিমেইলের সব শেষ হয়ে যায়, অটো নেক্সট জিমেইল চেক করবে
        if current_idx + 1 < len(state['email_list']):
            state['current_index'] += 1
            return get_gen_30_interface(chat_id)
        else:
            return "✅ <b>All Gmails Processed!</b>\nনতুন করে জিমেইল পাঠান।", main_menu()

    text = (f"🎯 <b>Active:</b> {current_base}\n"
            f"📊 <b>Queue:</b> {current_idx + 1}/{len(state['email_list'])}\n"
            f"📧 <b>Remaining: {len(variants)}</b>\n\n"
            f"<i>নিচের বাটনে ক্লিক করলে কপি মেসেজ আসবে এবং লিস্ট থেকে মুছে যাবে।</i>")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    # ১০টি করে ভ্যারিয়েন্ট বাটন দেখাবে যাতে স্ক্রিন বড় না হয়
    for i, mail in enumerate(variants[:10]):
        markup.add(types.InlineKeyboardButton(mail, callback_data=f"take_{i}"))
    
    # অতিরিক্ত কন্ট্রোল বাটন
    controls = []
    if len(state['email_list']) > 1:
        controls.append(types.InlineKeyboardButton("🔄 Switch Gmail", callback_data="switch_menu"))
    
    controls.append(types.InlineKeyboardButton("🔝 Main Menu", callback_data="back_to_main"))
    markup.add(*controls)
    
    return text, markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = ("🎉 <b>EMAIL VARIANT 6.9 BOT ACTIVE</b> 🤖\n\n"
                    "💥 <b>Created By</b> @Lohit_69💎\n\n"
                    "📥 <b>SEND AN EMAIL ADDRESS:</b>")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    
    if call.data == "mode_30":
        user_data[chat_id] = {'mode': '30'}
        bot.edit_message_text("📨 <b>GMAIL GEN 30 MODE</b>\n\nআপনি একসাথে ১ থেকে ৬টি জিমেইল দিতে পারেন।\n(জিমেইলগুলো স্পেস বা এন্টার দিয়ে আলাদা করে দিন)", chat_id, call.message.message_id)
    
    elif call.data == "mode_10k":
        user_data[chat_id] = {'mode': '10k'}
        bot.edit_message_text("📦 <b>GMAIL GEN 10K MODE</b>\n\nযেকোনো ১টি জিমেইল পাঠান। আমি ১০,০০০ ভ্যারিয়েন্ট ফাইল করে দিচ্ছি।", chat_id, call.message.message_id)

    elif call.data == "back_to_main":
        start_cmd(call.message)

    elif call.data == "switch_menu":
        state = user_data.get(chat_id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, email in enumerate(state['email_list']):
            prefix = "📍 " if i == state['current_index'] else ""
            markup.add(types.InlineKeyboardButton(f"{prefix}{email}", callback_data=f"set_idx_{i}"))
        bot.edit_message_text("🔍 <b>Select Gmail to Work:</b>", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("set_idx_"):
        idx = int(call.data.split("_")[2])
        user_data[chat_id]['current_index'] = idx
        text, markup = get_gen_30_interface(chat_id)
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("take_"):
        state = user_data.get(chat_id)
        idx = int(call.data.split("_")[1])
        current_base = state['email_list'][state['current_index']]
        
        # ১. আগের মেসেজ ডিলিট
        if state.get('last_copy_id'):
            try: bot.delete_message(chat_id, state['last_copy_id'])
            except: pass
        
        # ২. ভ্যারিয়েন্ট রিমুভ ও পাঠানো
        selected = state['variants_dict'][current_base].pop(idx)
        sent = bot.send_message(chat_id, f"<code>{selected}</code>")
        state['last_copy_id'] = sent.message_id
        
        # ৩. ইন্টারফেস আপডেট
        text, markup = get_gen_30_interface(chat_id)
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, "Copied!")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id)
    
    if not state or 'mode' not in state:
        bot.reply_to(message, "আগে নিচ থেকে একটি মোড সিলেক্ট করুন 👇", reply_markup=main_menu())
        return

    # --- Mode 30 Logic ---
    if state['mode'] == '30':
        emails = [e.strip() for e in message.text.replace('\n', ' ').split(' ') if '@' in e][:6]
        if not emails:
            bot.reply_to(message, "❌ সঠিক জিমেইল ফরম্যাট দিন!")
            return
        
        loading = bot.send_message(chat_id, "📧 <b>Processing Gmails...</b>")
        time.sleep(1)
        
        state['email_list'] = emails
        state['current_index'] = 0
        state['variants_dict'] = {e: generate_variants(e, 30) for e in emails}
        state['last_copy_id'] = None
        
        bot.delete_message(chat_id, loading.message_id)
        text, markup = get_gen_30_interface(chat_id)
        bot.send_message(chat_id, text, reply_markup=markup)

    # --- Mode 10K Logic ---
    elif state['mode'] == '10k':
        email = message.text.strip()
        if "@" not in email:
            bot.reply_to(message, "❌ Invalid Email!")
            return
        
        m1 = bot.send_message(chat_id, "📧 <b>Creating new account...</b>")
        time.sleep(1)
        bot.edit_message_text("⏳ <b>Please wait... generating 10K variants</b>", chat_id, m1.message_id)
        
        variants = generate_variants(email, 10000)
        file_buffer = io.BytesIO("\n".join(variants).encode('utf-8'))
        file_buffer.name = f"10K_{email.split('@')[0]}.txt"
        
        bot.edit_message_text("✅ <b>Account generated successfully!</b>", chat_id, m1.message_id)
        bot.send_document(chat_id, file_buffer, caption=f"🎯 Target: {email}\n📦 Total: 10,000", reply_markup=main_menu())

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
