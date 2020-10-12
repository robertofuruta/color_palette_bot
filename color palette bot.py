#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from colorpalette import color_palette_from_photo
from telegram.bot import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import io
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib
matplotlib.use('Agg')


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text("Hello there!\nI'm a bot capable of creating color palettes from images you send me!\nTo do so,\n1. Send me the image you want a collor palette from. Please send it as image, not file.\n2. Reply to the image you sent me with: '/palette' to get a 4 color palette or with '/palette N' replacing the N with the number of colors you want (between 2 and 10).\n\nThis is a experimental personal project, it may be offline, so I may not respond :c")


def help_command(update, context):
    update.message.reply_text("Hello there!\nI'm a bot capable of creating color palettes from images you send me!\nTo do so,\n1. Send me the image you want a collor palette from. Please send it as image, not file.\n2. Reply to the image you sent me with: '/palette' to get a 4 color palette or with '/palette N' replacing the N with the number of colors you want (between 2 and 10).\n\nThis is a experimental personal project, it may be offline, so I may not respond :c")


def unknown(update, context):
    update.message.reply_text("Huh?\nI don't know what you mean...")


def palette(update, context):
    print(update.message.from_user['username'],
          update.message.from_user['first_name'], update.message.from_user['last_name'])
    try:
        num_colors = int(context.args[0])
    except:
        num_colors = 4

    if num_colors not in range(2, 11):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Sorry, I only can generate 2 to 10 colors.")
        return

    media = update.message.reply_to_message.photo[0].get_file()
    # logging.info(f"{media}")
    if (media == None):
        return
    if (media.file_size > 15619356):
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Ok! i'm preparing your color palette with {num_colors} colors.")
    # context.bot.send_message(chat_id=update.effective_chat.id, text=f"{media.file_path}")

    media_id = media.file_id
    media_type = f"{media.file_path}".split('.')[-1]
    imageFile = context.bot.getFile(media_id)

    input_file = f'/tmp/{media_id}.{media_type}'
    imageFile.download(input_file)
    output_file = f'/tmp/out_{media_id}.{media_type}'
    success = False
    try:
        hex_colors = color_palette_from_photo(
            input_file, output_file, num_colors)
        os.remove(input_file)

        hex_colors_string = 'The colors are:\n'
        for i in range(num_colors):
            hex_colors_string += f'{hex_colors[i]}\n'
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=hex_colors_string)

        context.bot.send_photo(
            chat_id=update.effective_chat.id, photo=open(f"{output_file}", 'rb'))
        os.remove(output_file)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Sorry, something went wrong :c\nMaybe your image is too simple for me to find that many colors, try again with fewer.")
        print('uh oh :c')

    # context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(f"{output_file}", 'rb'))
    # os.remove(f"out-{fname}")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # with /
    token = open("telegram.token", "r").read()
    updater = Updater(token=token, use_context=True)
    # bot = Bot(token=token)
    # plot(bot,'@bananabacana')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("palette", palette, pass_args=True))
    dp.add_handler(MessageHandler(Filters.command, unknown)
                   )
    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()


if __name__ == '__main__':
    main()
