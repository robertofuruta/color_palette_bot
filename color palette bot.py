"""
This is a Telegram bot for generating color palettes from provided images.
To stop the bot, press Ctrl-C
"""

import io
import logging
import os
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from telegram.bot import Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from colorpalette import color_palette_from_photo

matplotlib.use('Agg')


# Updates de logging and sends the entry to the private logging channel.
def log(context, log_entry):
    logging.info(log_entry)
    context.bot.send_message(chat_id=channel_chat_id,
                             text=log_entry)
    return


def start(update, context):
    update.message.reply_text("""Hello there!
I'm a bot capable of creating color palettes from images you send me!
To do so,
1. Send me the image you want a collor palette from.
2. Reply to the image you sent me with: '/palette' to get a 5 color palette or with '/palette N' \
replacing the N with the number of colors you want (between 2 and 10).
This is a experimental personal project, it may be offline, so I may not respond :c""")


def help_command(update, context):
    update.message.reply_text("""Hello there!
I'm a bot capable of creating color palettes from images you send me!
To do so,
1. Send me the image you want a collor palette from.
2. Reply to the image you sent me with: '/palette' to get a 5 color palette or with '/palette N' \
replacing the N with the number of colors you want (between 2 and 10).
This is a experimental personal project, it may be offline, so I may not respond :c""")


def unknown(update, context):
    update.message.reply_text("Huh?\nI don't know what you mean...")


def palette(update, context):
    request_str = f"@{update.message.from_user['username']}: {update.message.from_user['first_name']} {update.message.from_user['last_name']} requested a plaette..."
    log(context, request_str)

    try:
        num_colors = int(context.args[0])
    except:
        num_colors = 5
    if num_colors not in range(2, 11):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Sorry, I only can generate 2 to 10 colors.")
        log(context, f'Falied: wrong N: {num_colors}.')
        return

    try:
        resolutions = len(update.message.reply_to_message.photo)
        print('ress', resolutions)
        media = update.message.reply_to_message.photo[resolutions-1].get_file()
    except:
        try:
            media = update.message.reply_to_message.document.get_file()
        except:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Hey, thet's not and image! :|\nYou have to first send me an image, than reply to it with that command ;)")
            log(context, 'Falied: not an image.')
            return
    media_id = media.file_id
    media_type = f"{media.file_path}".split('.')[-1]
    if not media_type in ['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG']:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"I don't regnize this file as an image, sorry :/\nI only know how to precess png and jpg images!")
        log(context, 'Falied: not an image.')
        return

    if (media == None):
        return
    if (media.file_size > 10**6):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Wow that's large!\nI can't deal with that!! (over 10MB)\nYou can compress it's size by sending it as image, not as document.")
        log(context, 'Falied: too large.')
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Ok! i'm preparing your color palette with {num_colors} colors.")

    imageFile = context.bot.getFile(media_id)

    directory = 'tmp/'
    if not os.path.exists(directory):
        os.mkdir(directory)

    input_file = f'{directory}{media_id}.{media_type}'
    imageFile.download(input_file)
    output_file = f'{directory}out_{media_id}.{media_type}'

    # try:
    hex_colors = color_palette_from_photo(
        input_file, output_file, num_colors, select=True)
    os.remove(input_file)

    hex_colors_string = 'The colors are:\n'
    for i in range(num_colors):
        hex_colors_string += f'{hex_colors[i]}\n'
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=hex_colors_string)

    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(f"{output_file}", 'rb'))
    os.remove(output_file)
    log(context, 'Done successfuly.')


def main():

    # Enable logging
    logging.basicConfig(filename='color_palette_bot.log',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
                        )

    logger = logging.getLogger(__name__)

    token = open("telegram.token", "r").read()
    global channel_chat_id
    channel_chat_id = open("channel_chat.id", "r").read()
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("palette", palette, pass_args=True))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()
    log(updater, "Booting up...")
    updater.idle()
    log(updater, "Good bye!")


if __name__ == '__main__':
    main()
