# telegram.me/ColorPaletteFromImageBot

*A telegram bot for generating color palettes from images.*

Link: 
<blockquote>
https://telegram.me/ColorPaletteFromImageBot
</blockquote>

or search for 
<blockquote>
<b>@ColorPaletteFromImageBot</b>
</blockquote>
on your Telegram.


To use it:
<blockquote>

- Send the source image to the bot.

- Repy to the sent image with the command <b> /palette </b> to get a 5 color palette or with <b> /palette N </b> replacing the N with the number of colors you want (between 2 and 10).

- *I don't have a propper server set up, if it doesn't respond, it's because it's offline.*</blockquote>



This is built in Python3, mainly using the python_telegram_bot library.

The colors for the palette are found by applying the k-means clustering method on the vector of pixels of the image. Currently, this is done over the hue, saturation, value color space. 2*N cores are found this way, and the best of them are chosen.

