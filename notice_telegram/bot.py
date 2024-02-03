import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


# App contsants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TARGET_URL = os.getenv("TARGET_URL")


# Check constants
if not TELEGRAM_BOT_TOKEN:
    exit("Specify TELEGRAM_BOT_TOKEN env variable")

if not TARGET_URL:
    exit("Specify TARGET_URL env variable")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Define handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет")
    
async def subscribe(update, context):
    # Get the parameters passed with the command
    # For example, /custom_command parameter1 parameter2
    parameters = context.args
    if not parameters:
        await update.message.reply_text('No parameters provided for the command.')
    else:
        await update.message.reply_text(f'Command received with parameters: {", ".join(parameters)}')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    conversation_handler = ConversationHandler()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    
    application.run_polling()
