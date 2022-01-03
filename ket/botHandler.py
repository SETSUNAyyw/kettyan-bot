# -*- coding: UTF-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, InputMediaPhoto, Dice

from ket.pixivHelper import *

from time import time
from requests.exceptions import Timeout, SSLError

import re


def logUser(message):
	id_from = message.from_user.id
	name_from = message.from_user.username
	first_name_from = message.from_user.first_name
	last_name_from = message.from_user.last_name
	log_user = str(id_from) + ":" + str(name_from) + ",\"" + str(first_name_from) + " " + str(last_name_from) + "\""
	return log_user

def echo(update: Update, context: CallbackContext):
	log_user = logUser(update.message)
	start = time()
	pid = update.message.text
	args = []
	page = 0
	if (not pid.isdigit()):
		args = pid.split(" ")
		if (not args):
			context.bot.send_message(chat_id = update.effective_chat.id, text = "何を言っているのかわからないニャ！")
			print("[{}] Illegal Message: {}".format(log_user, pid))
			return
		else:
			inline_id_found = False
			for arg in args:
				inline_id = re.findall(r".*?pixiv.net/artworks/(\d+)", arg)
				if (inline_id):
					pid = inline_id[0]
					inline_id_found = True
					break
			if (inline_id_found):
				print("[{}] Inline pixiv link detected.".format(log_user))
			else:
				print("[{}] Searching for tags {}...".format(log_user, args))
				infos = fetchLolicon(args = args)
				infos_keyword = []
				if (infos):
					print("[{}] Good tags.".format(log_user))
					pid, page, hoge = infos[0]
				else:
					print("[{}] Bad tags. Searching for keyword {} instead...".format(log_user, args[0]))
					if (len(args) > 1):
						infos_keyword = fetchLolicon(args = args[1:], keyword = args[0])
					else:
						infos_keyword = fetchLolicon(keyword = args[0])
				if (infos_keyword):
					print("[{}] Good keyword.".format(log_user))
					pid, page, hoge = infos_keyword[0]
				elif (not infos):
					context.bot.send_message(chat_id = update.effective_chat.id, text = "検索結果が見つかりませんでした…")
					print("[{}] Invalid tags/keyword {}.".format(log_user, args))
					return
	url = "https://pixiv.cat/" + pid + ".jpg"
	try:
		valid_pid, url = urlIsImage(url)
	except (SSLError, Timeout):
		print("[{}][Error] SSLError/Timeout caught in fetching {}, operation failed.".format(log_user, url))
		context.bot.send_message(chat_id = update.effective_chat.id, text = "不明なエラーが発生しました。もう一度試してください")
		return
	demo_url = "https://www.pixiv.net/artworks/" + pid
	if (valid_pid):
		try:
			demo_caption = crawlPixivInfo(pid)
		except Timeout:
			print("[{}][Warning] Gathering pixiv info of {} timeout. Aborting...".format(log_user, pid))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "タイムアウトしました。")
			return
		try:
			downloadPath = downloadImage(url, pid, page)
			context.bot.send_photo(chat_id = update.effective_chat.id, photo = open(downloadPath, "rb"), caption = demo_caption, parse_mode = "HTML")
		except Timeout:
			print("[{}][Warning] Download of {} timeout. Aborting...".format(log_user, url))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "タイムアウトしました。")
			return
		except SSLError:
			print("[{}][Error] SSLError caught in fetching {}, operation failed.".format(log_user, url))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "不明なエラーが発生しました。もう一度試してください")
		except Exception:
			print("[{}][Error] Unknown error in fetching {} from telegram server.".format(log_user, url))
			context.bot.send_message(chat_id = update.effective_chat.id, text = demo_url)
		end = time()
		print("[{}] Fetched PID {} in {:.2f}s, num: {}.".format(log_user, pid, end - start, 1))
		return

	url = "https://pixiv.cat/" + pid + "-1.jpg"
	try:
		valid_pid, url = urlIsImage(url)
	except (SSLError, Timeout):
		print("[{}][Error] SSLError/Timeout caught in fetching {}, operation failed.".format(log_user, url))
		context.bot.send_message(chat_id = update.effective_chat.id, text = "不明なエラーが発生しました。もう一度試してください")
		return
	if (valid_pid):
		try:
			demo_caption = crawlPixivInfo(pid)
		except Timeout:
			print("[{}][Warning] Gathering pixiv info of {} timeout. Aborting...".format(log_user, pid))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "タイムアウトしました。")
			return
		media_json = []
		urls = []
		pids = []
		pages = []
		i = 1
		for i in range(1, 11, 1):
			if (i > 1):
				url = "https://pixiv.cat/" + pid + "-" + str(i) + ".jpg"
				try:
					valid_pid, url = urlIsImage(url)
				except (SSLError, Timeout):
					print("[{}][Error] SSLError/Timeout caught in fetching {}, operation continued.".format(log_user, url))
					continue
			if (valid_pid):
				urls.append(url)
				pids.append(pid)
				pages.append(i)
			else:
				break
			if (i == 10):
				print("[{}][Warning] Too much pictures in PID {}, only send 10 of them.".format(log_user, pid))
		try:
			downloadPaths = downloadImage(urls, pids, pages)
		except Timeout:
			print("[{}][Warning] Download of {} timeout. Aborting...".format(log_user, url))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "タイムアウトしました。")
		except SSLError:
			print("[{}][Error] SSLError caught in fetching {}, operation continued.".format(log_user, url))
		for downloadPath in downloadPaths:
			if (media_json):
				media_json.append(InputMediaPhoto(media = open(downloadPath, "rb")))
			else:
				media_json.append(InputMediaPhoto(media = open(downloadPath, "rb"), caption = demo_caption, parse_mode = "HTML"))
		if (not media_json):
			print("[{}][Error] Unknown error in downloading all images {}.".format(log_user, pid))
			context.bot.send_message(chat_id = update.effective_chat.id, text = "不明なエラーが発生しました。もう一度試してください")
			return
		try:
			context.bot.send_media_group(chat_id = update.effective_chat.id, media = media_json)
		except Exception:
			print("[{}][Error] Unknown error in fetching {} from telegram server.".format(log_user, url))
			context.bot.send_message(chat_id = update.effective_chat.id, text = demo_url)
		end = time()
		print("[{}] Fetched PID {} in {:.2f}s, num: {}.".format(log_user, pid, end - start, i - 1))
		return

	context.bot.send_message(chat_id = update.effective_chat.id, text = "検索結果が見つかりませんでした…")
	print("[{}] Invalid PID {}.".format(log_user, pid))

def start(update: Update, context: CallbackContext):
	id_from = update.message.from_user.id
	name_from = update.message.from_user.username
	first_name_from = update.message.from_user.first_name
	last_name_from = update.message.from_user.last_name
	log_user = str(id_from) + ":" + str(name_from) + ",\"" + str(first_name_from) + " " + str(last_name_from) + "\""
	if (last_name_from):
		start_text = "{} ".format(last_name_from)
	else:
		start_text = ""
	start_text += "{}さん、よろしくお願いしますね！使い方は /help で".format(first_name_from)
	context.bot.send_message(chat_id = update.effective_chat.id, text = start_text)
	print("[{}] Started.".format(log_user))

def helper(update: Update, context: CallbackContext):
	log_user = logUser(update.message)
	help_text = ("Pixiv ID/タグ/検索内容を送ってください\n"
		"コマンドリスト：\n"
		"/start - 挨拶をする\n"
		"/help - 使い方を見る\n"
		"/r0 <n> - ランダム画像n枚（default = 1）\n"
		"/r18 <n> - ランダム18禁画像n枚（default = 1）\n"
		"/d - サイコロを振る")
	context.bot.send_message(chat_id = update.effective_chat.id, text = help_text)
	print("[{}] Helped.".format(log_user))

def dice(update: Update, context: CallbackContext):
	log_user = logUser(update.message)
	dice = context.bot.send_dice(chat_id = update.effective_chat.id).dice.value
	print("[{}] Diced {}.".format(log_user, dice))

def randomImage(update: Update, context: CallbackContext, r_18 = False):
	log_user = logUser(update.message)
	n_pic = context.args

	if (n_pic):
		n_pic = n_pic[0]
		if (not n_pic.isdigit()):
			context.bot.send_message(chat_id = update.effective_chat.id, text = "/r0 <number>: numberは1~10の整数")
			print("[{}] Randomed invalid arguments {}.".format(log_user, context.args))
			return
		else:
			n_pic = int(n_pic)
	else:
		n_pic = 1
	if ((n_pic > 10) | (n_pic < 1)):
		context.bot.send_message(chat_id = update.effective_chat.id, text = "/r0 <number>: numberは1~10の整数")
		print("[{}] Randomed invalid arguments {}.".format(log_user, context.args))
		return

	pic_fetched = 0
	print("[{}] Called {} {}random.".format(log_user, n_pic, "R-18 " if (r_18) else ""))
	print("[{}] Fetching {} data from lolicon api...".format(log_user, n_pic))
	infos = fetchLolicon(n_pic, r_18 = r_18)
	print("[{}] Success. {} pids fetched.".format(log_user, len(infos)))
	start = time()
	while (True):
		demo_captions = []
		urls = []
		pids = []
		pages = []
		for pid, page, url in infos:
			print("[{}] Target url: {}".format(log_user, url))
			try:
				valid_pid, hoge = urlIsImage(url)
			except (SSLError, Timeout):
				print("[{}][Error] SSLError/Timeout caught in fetching {}, operation continued.".format(log_user, url))
				continue
			demo_url = "https://www.pixiv.net/artworks/" + pid
			if (valid_pid):
				try:
					demo_caption = crawlPixivInfo(pid)
				except Timeout:
					print("[{}][Warning] Gathering pixiv info of {} timeout. Aborting...".format(log_user, pid))
					continue
				demo_captions.append(demo_caption)
				urls.append(url)
				pids.append(pid)
				pages.append(page)

		try:
			downloadPaths = downloadImage(urls, pids, pages)
		except Exception:
			for url in urls:
				print("[{}][Error] Unknown error in fetching {} from telegram server.".format(log_user, url))
				context.bot.send_message(chat_id = update.effective_chat.id, text = demo_url)
				pic_fetched = pic_fetched + 1
		if (isinstance(downloadPaths, str)):
			downloadPaths = [downloadPaths]
		for downloadPath, demo_caption in zip(downloadPaths, demo_captions):
			context.bot.send_photo(chat_id = update.effective_chat.id, photo = open(downloadPath, "rb"), caption = demo_caption, parse_mode = "HTML")
			pic_fetched = pic_fetched + 1
		if (pic_fetched < n_pic):
			print("[{}] Refetching {} data from lolicon api...".format(log_user, (n_pic - pic_fetched)))
			infos = fetchLolicon(n_pic - pic_fetched, r_18 = r_18)
			print("[{}] Success. {} pids refetched.".format(log_user, len(infos)))
		else:
			end = time()
			print("[{}] Fetched {} pics in {:.2f}s.".format(log_user, pic_fetched, end - start))
			break
