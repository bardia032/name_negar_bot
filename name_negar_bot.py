import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
import openai
import datetime
from persiantools.jdatetime import JalaliDate
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
import asyncio
import logging

logging.basicConfig(filename='bot_log.txt', level=logging.INFO)

# Define conversation states
RECIPIENT, TEXT, SIGN, TONE = range(4)

# Set your OpenAI API key here
openai.api_key = "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"

# Set your Telegram bot API here
myBot = Bot ("6590375844:AAEecUH0x1kspoKxOUy3r82PqACvnRjEs0E")

# Dictionary to map user-friendly tone names to GPT-3 prompts
tone_prompts = {
    'رسمی': 'Generate a formal letter in persian:\n\n',
    'دوستانه': 'Generate a friendly letter in persian:\n\n',
    'با عصبانیت': 'Generate an angry letter in persian:\n\n',
    'با قید فوریت': 'Generate an urgent letter in persian:\n\n'
}


def start(update: telegram.Update, context: CallbackContext):
    update.message.reply_text(
        "سلام\nمن در نوشتن نامه به شما کمک می‌کنم\n"
        "لطفاً نام گیرنده یا گیرندگان را در خطوط جداگانه وارد کنید:"
    )
    return RECIPIENT

def collect_recipient(update: telegram.Update, context: CallbackContext):
    recipients = update.message.text.split('\n')
    context.user_data['recipients'] = recipients
    update.message.reply_text("متن نامه را وارد کنید:")
    return TEXT

def collect_text(update: telegram.Update, context: CallbackContext):
    context.user_data['text'] = update.message.text
    update.message.reply_text("لطفاً نام خود را وارد کنید:")
    return SIGN

def collect_sign(update: telegram.Update, context: CallbackContext):
    context.user_data['sign'] = update.message.text

    # Create a custom keyboard with tone options
    reply_keyboard = [['رسمی', 'دوستانه'], ['با عصبانیت', 'با قید فوریت']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=markup,
    )

    return TONE

def collect_tone(update: telegram.Update, context: CallbackContext):
    tone = update.message.text
    user_data = context.user_data

    # Construct the letter text
    recipients = '\n'.join([f"**گیرنده:** {recipient}" for recipient in user_data['recipients']])
    letter = f"{recipients}\n\n"
    letter += f"با سلام؛\n\n{user_data['text']}\n\nبا سپاس\n{user_data['sign']}\n"

    # Define the GPT-3 prompt based on the selected tone
    if tone == 'رسمی':
        prompt = f"Generate a formal letter in persian:\n\n{letter}"
    elif tone == 'دوستانه':
        prompt = f"Generate a friendly letter in persian:\n\n{letter}"
    elif tone == 'با عصبانیت':
        prompt = f"Generate an angry letter in persian:\n\n{letter}"
    elif tone == 'با قید فوریت':
        prompt = f"Generate an urgent letter in persian:\n\n{letter}"

    # Send the prompt to GPT-3 and receive the response
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=3000  # You can adjust this based on your desired letter length
    )

    modified_letter = response.choices[0].text

    # Get the current Jalali date
    jalali_date = JalaliDate(datetime.date.today()).strftime('%d %B %Y')

    # Combine the modified letter with the current Jalali date
    final_letter = f"{modified_letter}\n{jalali_date}"

    # Send the final letter to the user
    update.message.reply_text(final_letter, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def main():

    myUpdateQueue = asyncio.Queue()
    updater = Updater(bot=myBot, update_queue=myUpdateQueue)

    # Initialize the updater
    await updater.initialize()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('/start', start)],
        states={
            RECIPIENT: [MessageHandler(filters.TEXT, collect_recipient)],
            TEXT: [MessageHandler(filters.TEXT, collect_text)],
            SIGN: [MessageHandler(filters.TEXT, collect_sign)],
            TONE: [MessageHandler(filters.TEXT, collect_tone)],
        },
        fallbacks=[],
    )

    await updater.start_polling()

    while True:
        await asyncio.sleep(1) 

if __name__ == '__main__':
   asyncio.run(main())
