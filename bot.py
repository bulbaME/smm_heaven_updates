import logging
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, JobQueue
import yaml
import updates

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CRED = yaml.safe_load(open('credentials.yaml'))['TELEGRAM']
TOKEN = CRED['TOKEN']
CHAT_ID = CRED['CHAT_ID']

async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    u = updates.get_updates()

    s = ''
    for update in u:
        s += f'{update[0]}\n{update[1]}\nDate: {update[2]}\n\n'

    await context.bot.send_message(CHAT_ID, s)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)

def init():
    application = ApplicationBuilder().token(TOKEN).build()
    application.job_queue.run_repeating(send_updates, 300)

    # start_hndl = CommandHandler('start', start)
    # application.add_handler(start_hndl)

    application.run_polling(timeout=60, pool_timeout=30)