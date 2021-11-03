import logging
import os
import sys

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

load_dotenv()

token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR,
    handlers=[logging.StreamHandler(stream=sys.stdout),
              logging.FileHandler(filename=__name__.strip('__') + '.log')]
)

URL_CAT = 'https://api.thecatapi.com/v1/images/search'
URL_QUOTE = 'https://bash.im/forweb/?u'


def corrector(text):
    num = text.find('#21201e"') + 9
    text = text[num:]
    num = text.find("<' + '/div>")
    text = text[:num]
    text = text.replace("<' + 'br>", "\n")
    text = text.replace("&quot;", '"')
    return text


def get_new_image():
    try:
        response = requests.get(URL_CAT)
    except Exception as e:
        logging.error(f'Ошибка при запросе к основному API: {e}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_new_quote():
    try:
        response = requests.get(URL_QUOTE)
    except Exception as e:
        logging.error(f'Ошибка при запросе к bash: {e}')
        response = 'Новой цитаты не будет :( Попробуй позже'
    text = response.text
    if isinstance(response, str):
        return text
    return corrector(text)


def new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def new_quote(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_quote())


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/newcat'], ['/newquote']],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}! Посмотри какого котика я тебе нашёл!'.format(name),
        reply_markup=button
    )
    context.bot.send_photo(chat.id, get_new_image())


def main():
    updater = Updater(token=token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('newquote', new_quote))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
