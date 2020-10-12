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
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from colorpalette import color_palette_from_photo

matplotlib.use('Agg')


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers.
def start(update, context):
    update.message.reply_text("""Hello there!
I'm a bot capable of creating color palettes from images you send me!
To do so,
1. Send me the image you want a collor palette from. Please send it as image, not file.
2. Reply to the image you sent me with: '/palette' to get a 4 color palette or with '/palette N' \
replacing the N with the number of colors you want (between 2 and 10).
This is a experimental personal project, it may be offline, so I may not respond :c""")


def help_command(update, context):
    update.message.reply_text("""Hello there!
I'm a bot capable of creating color palettes from images you send me!
To do so,
1. Send me the image you want a collor palette from. Please send it as image, not file.
2. Reply to the image you sent me with: '/palette' to get a 4 color palette or with '/palette N' \
replacing the N with the number of colors you want (between 2 and 10).
This is a experimental personal project, it may be offline, so I may not respond :c""")


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

    if (media == None):
        return
    if (media.file_size > 15619356):
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Ok! i'm preparing your color palette with {num_colors} colors.")

    media_id = media.file_id
    media_type = f"{media.file_path}".split('.')[-1]
    imageFile = context.bot.getFile(media_id)

    input_file = f'/tmp/{media_id}.{media_type}'
    imageFile.download(input_file)
    output_file = f'/tmp/out_{media_id}.{media_type}'

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


def main():
    token = open("telegram.token", "r").read()
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("palette", palette, pass_args=True))
    dp.add_handler(MessageHandler(Filters.command, unknown)
                   )
    # Start the Bot
    updater.start_polling()


if __name__ == '__main__':
    main()
