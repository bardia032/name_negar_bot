import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import openai

# Define conversation states
RECIPIENT, TEXT, DATE, SIGN, TONE = range(5)

# Set your OpenAI API key here
openai.api_key = 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

def start(update, context):
    update.message.reply_text("سلام! من می‌توانم به شما در نوشتن یک نامه کمک کنم. نام گیرنده یا گیرنده‌ها را با / جدا کنید :")
    return RECIPIENT

def collect_recipient(update, context):
    recipients = update.message.text.split('/')
    context.user_data['recipients'] = recipients
    update.message.reply_text("عالی! متن نامه را وارد کنید:")
    return TEXT

def collect_text(update, context):
    context.user_data['text'] = update.message.text
    update.message.reply_text("تاریخ نامه را وارد کنید:")
    return DATE

def collect_date(update, context):
    context.user_data['date'] = update.message.text
    update.message.reply_text("و در آخر، لطفاً امضای خود را وارد کنید.")
    return SIGN

def collect_sign(update, context):
    context.user_data['sign'] = update.message.text
    update.message.reply_text("لطفاً تنها یکی از تنهاهای زیر را انتخاب کنید: رسمی، دوستانه، فوری، خشمگین.")
    return TONE

def collect_tone(update, context):
    tone = update.message.text
    user_data = context.user_data

    # Send user's request to GPT-3 for processing and get the modified letter
    modified_letter = send_to_gpt(user_data, tone)

    # Send the modified letter back to the user
    update.message.reply_text("درخواست شما پردازش شد و نامه ویرایش شده به شما ارسال می‌شود:\n\n" + modified_letter)

    return ConversationHandler.END

def send_to_gpt(user_data, tone):
    # Construct the letter text with recipients, با سلام, user's text, با سپاس, signature, and Shamsi date
    recipients = '\n'.join([f"**گیرنده:** {recipient}" for recipient in user_data['recipients']])
    letter = f"{recipients}\n\n"
    letter += "**با سلام؛**\n\n"
    letter += user_data['text'] + "\n\n"
    letter += "**با سپاس**\n\n"
    letter += user_data['sign'] + "\n\n"
    letter += user_data['date']

    # Define the GPT-3 prompt based on the selected tone
    if tone == 'فرمال':
        prompt = f"Generate a formal letter in persian:\n\n{letter}"
    elif tone == 'دوستانه':
        prompt = f"Generate a friendly letter in persian:\n\n{letter}"
    elif tone == 'فوری':
        prompt = f"Generate an urgent letter in persian:\n\n{letter}"
    elif tone == 'خشمگین':
        prompt = f"Generate an angry letter in persian:\n\n{letter}"

    # Send the prompt to GPT-3 and receive the response
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150  # You can adjust this based on your desired letter length
    )

    return response.choices[0].text

def main():
    updater = Updater(token=6590375844:AAEecUH0x1kspoKxOUy3r82PqACvnRjEs0E, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RECIPIENT: [MessageHandler(Filters.text, collect_recipient)],
            TEXT: [MessageHandler(Filters.text, collect_text)],
            DATE: [MessageHandler(Filters.text, collect_date)],
            SIGN: [MessageHandler(Filters.text, collect_sign)],
            TONE: [MessageHandler(Filters.text, collect_tone)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
