import logging
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, JobQueue, CommandHandler, MessageHandler, filters
import yaml
import updates

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CRED = yaml.safe_load(open('credentials.yaml'))['TELEGRAM']
TOKEN = CRED['TOKEN']
CHAT_ID = CRED['CHAT_ID']
MONK_ID = CRED['MONK_ID']

async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.bot_data['logged']:
            return
    except:
        pass

    u = updates.get_updates()

    if u == None:
        driver = updates.get_driver()
        driver.get(updates.URL)
        context.bot_data['driver'] = driver
        context.bot_data['logged'] = False
        updates.login(driver)
        await context.bot.send_message(MONK_ID, 'Send authenthication code')

        return

    context.bot_data['logged'] = True

    s = ''
    for update in u:
        s += f'{update[0]}\n{update[1]}\nDate: {update[2]}\n\n'

    if len(s) > 0:
        await context.bot.send_message(CHAT_ID, s)

async def auth_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.bot_data['logged']:
        return
    
    code = update.message.text.strip()

    if not updates.enter_passcode(context.bot_data['driver'], code):
        await context.bot.send_message(MONK_ID, 'Wrong code, try again')
        return
    
    context.bot_data['logged'] = True
    context.bot_data['driver'].quit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)

def init():
    application = ApplicationBuilder().token(TOKEN).build()
    application.job_queue.run_repeating(send_updates, 300)

    auth_code_hndl = MessageHandler(filters.TEXT, auth_code)
    application.add_handler(auth_code_hndl)

    # start_hndl = CommandHandler('start', start)
    # application.add_handler(start_hndl)

    application.run_polling(timeout=60, pool_timeout=30)