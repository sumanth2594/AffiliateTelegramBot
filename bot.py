# bot.py
import telegram as tg
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import MessageEntity
import re
import requests
import os
import pyshorteners
s = pyshorteners.Shortener(api_key='BITLYTOKEN')
print(s)
url = "https://www.amazon.in/dp/B089MS8VY3/ref=s9_acsd_al_bw_c2_x_1_i?pf_rd_m=A1K21FY43GMZF8&pf_rd_s=merchandised-search-3&pf_rd_r=G03ZN4RS5QE79BMHRZP1&pf_rd_t=101&pf_rd_p=8bb85f20-458f-44ca-b5c2-e95db3f72e29&pf_rd_i=23023572031"
a = s.bitly.short(url)
print("Printing the short url", a)
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
#Read env variables
TOKEN = os.environ['TOKEN']
baseURL = os.environ['baseURL']
affiliate_tag = os.environ['affiliate_tag']
HEROKU_URL = os.environ['HEROKU_URL']
BITLYTOKEN = os.environ['BITLYTOKEN']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Este bot responde a los enlaces de amazon añadiendo un codigo de afiliado!")

# Create the new URL with the refer tag
def newReferURL(pcode):
    return baseURL+pcode+"?tag="+affiliate_tag

#Expand shorted URL (amzn.to links) to normal Amazon URL
def unshortURL(url):
    session = requests.Session()  # so connections are recycled
    resp = session.head("https://"+url, allow_redirects=True)
    return resp.url

#Filter the msg text to extract the URL if found. Then send the corresponding reply
# with the new affiliate URL
def filterText(update, context):
    pCode=""
    msg = update.message.text
    start = msg.find("amzn.to")
    if start!=-1:
        msg = unshortURL(msg[start:].split()[0])
    start = msg.find(baseURL)
    if start != -1:
        #Regular expression to extract the product code. Adjust if different URL schemes are found.
        m = re.search(r'(?:dp\/[\w]*)|(?:gp\/product\/[\w]*)',msg[start:].split(" ")[0])
        if m != None:
            pCode = m.group(0)
        context.bot.send_message(chat_id=update.message.chat_id,reply_to_message_id=update.message.message_id, text=newReferURL(pCode))

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(
                   Filters.text & (Filters.entity(MessageEntity.URL) |
                                    Filters.entity(MessageEntity.TEXT_LINK)),filterText))
    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(HEROKU_URL + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()