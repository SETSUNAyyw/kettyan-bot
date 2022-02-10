# -*- coding: UTF-8 -*-
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# from telegram import Update, InputMediaPhoto, Dice
# from getImageInfo import getImageInfo

from ket.bot import *

import threading
import requests
import os
import time


def printit():
	threading.Timer(1740, printit).start()
	print("Bot active.")

def clearCache():
	threading.Timer(7200, clearCache).start()
	for f in os.listdir("img"):
		file_path = os.path.join("img", f)
		if (os.path.isfile(file_path)):
			os.remove(file_path)
	for f in os.listdir("data"):
		file_path = os.path.join("data", f)
		if ((time.time() - os.stat(file_path).st_mtime > 3600)
			& (os.path.isfile(file_path))):
			os.remove(file_path)
	print("Cache cleared.")

def main():
	printit()
	if (not os.path.exists("img")):
		os.mkdir("img")
	if (not os.path.exists("data")):
		os.mkdir("data")
	clearCache()
	with open("token.txt", "r") as f:
		token = f.readline()
	updater = Updater(token = token, workers = 16)
	dispatcher = updater.dispatcher
	print("Bot started.")	

	start_handler = CommandHandler('start', start, run_async = True)
	dispatcher.add_handler(start_handler)
	help_handler = CommandHandler('help', helper, run_async = True)
	dispatcher.add_handler(help_handler)
	dice_handler = CommandHandler('d', dice, run_async = True)
	dispatcher.add_handler(dice_handler)
	random_handler = CommandHandler('r0', lambda update, context: randomImage(update, context), pass_args = True, run_async = True)
	dispatcher.add_handler(random_handler)
	random_kin_handler = CommandHandler('r18', lambda update, context: randomImage(update, context, r_18 = True), pass_args = True, run_async = True)
	dispatcher.add_handler(random_kin_handler)
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo, run_async = True)
	dispatcher.add_handler(echo_handler)
	sticker_handler = MessageHandler(Filters.sticker, stickerConverter, run_async = True)
	dispatcher.add_handler(sticker_handler)
	photo_handler = MessageHandler(Filters.photo, imageSearch, run_async = True)
	dispatcher.add_handler(photo_handler)
	callback_handler = CallbackQueryHandler(callback)
	dispatcher.add_handler(callback_handler)

	updater.start_polling()
	updater.idle()

def test():
	# url = "https://i.pixiv.cat/img-master/img/2020/12/07/20/56/37/86157915_p1_master1200.jpg"
	url = "https://www.pixiv.net/86157915"
	# pid = re.findall(r"https://pixiv.net/artworks/(\d+)", url))
	# print(pid)
	# html = requests.get(url, headers={"Range": "50"})
	html = requests.get(url)
	html_dic = eval(str(html.headers))
	# url = html_dic["X-Origin-URL"]
	# url = url.rstrip(".jpg")
	# r_check = requests.get(url, headers={"Range": "50"})
	# image_info = getImageInfo(r_check.content)
	print(html_dic)
	# print(image_info)


if __name__ == '__main__':
	main()
	# test()