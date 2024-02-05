#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Application class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Note:
To use the JobQueue, you must install PTB via
`pip install "python-telegram-bot[job-queue]"`
"""

import logging
import sqlite3
import httpx
import os

from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Application, 
    ContextTypes,
    filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set and <cookie> next message to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    URL = "https://cmr24.by/account/search?version=1"
    headers = {"Cookie": job.data}

    res = httpx.get(URL, headers=headers)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    list = []
    inserted = []

    for row in soup.find_all("tr", class_="search-table-mobile-size"):
        list.append(row.get('trid'))

    con = sqlite3.connect("./db.sqlite3")
    cur = con.cursor()
    for row in list:
        cur.execute("INSERT OR IGNORE INTO trid VALUES(?) RETURNING id", (row,))
        res = cur.fetchone()
        if res:
            inserted.append(res)

    con.commit()
    con.close()

    logger.info(inserted)

    if len(inserted):
        await context.bot.send_message(job.chat_id, text=f"Beep! check your list!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point."""

    return 0


async def create_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_repeating(alarm, 30, chat_id=chat_id, name=str(chat_id), data=update.message.text)

    await update.effective_message.reply_text("""job successfully created.""")
    
    return ConversationHandler.END


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("set", set_timer)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_job)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("unset", unset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def initDB() -> None:
    con = sqlite3.connect("./db.sqlite3")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS trid(id INTEGER PRIMARY KEY)")
    con.commit()
    con.close()
 


if __name__ == "__main__":
    initDB()
    main()
