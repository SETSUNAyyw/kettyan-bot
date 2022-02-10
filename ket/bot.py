# -*- coding: UTF-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram import Update, InputMediaPhoto, Dice, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from ket.http import *

from time import time
from PIL import Image
from requests.exceptions import Timeout, SSLError

import re
import threading


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
	help_text = ("<a>検索内容を送ってください\n"
		"<a href='https://remisiki.github.io/kettyan-bot/'>詳しく(English/日本語/中文)</a>\n"
		"/start - 挨拶をする\n"
		"/help - 使い方を見る\n"
		"/r0 - ランダム画像\n"
		"/r18 - ランダム18禁画像\n"
		"/d - サイコロを振る</a>")
	context.bot.send_message(chat_id = update.effective_chat.id, text = help_text, parse_mode = "HTML")
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

def stickerConverter(update: Update, context: CallbackContext):
	log_user = logUser(update.message)
	file_id = update.message.sticker.file_id
	file_is_webp = (not update.message.sticker.is_animated)
	if (file_is_webp):
		sticker_file = context.bot.get_file(file_id = file_id)
		webp_path = f"img/sticker{file_id}.webp"
		png_path = f"img/sticker{file_id}.png"
		if (not os.path.exists(webp_path)):
			sticker_file.download(webp_path)
		sticker_file = Image.open(webp_path).convert("RGBA")
		if (not os.path.exists(png_path)):
			sticker_file.save(png_path, "png")
		context.bot.send_document(chat_id = update.effective_chat.id, document = open(png_path, "rb"))
		context.bot.send_photo(chat_id = update.effective_chat.id, photo = open(png_path, "rb"))
		print("[{}] Returning sticker {}.".format(log_user, file_id))
	else:
		print("[{}] Sticker {} is animated.".format(log_user, file_id))

def imageSearch(update: Update, context: CallbackContext):
	log_user = logUser(update.message)
	print(f"[{log_user}] Started image searching.")
	file_id = update.message.photo[-1].file_id
	image_path = os.path.join("img", f"{update.message.chat.id}_{update.message.message_id}.jpg")
	context.bot.get_file(file_id).download(image_path)
	try:
		links, similarities = saucenaoSearch(image_path)
	except Exception as e:
		context.bot.send_message(chat_id = update.effective_chat.id, text = "サーバー側で障害が発生しています…")
		print(f"[{log_user}] Saucenao error {e}.")
		return

	threads = []
	additional_links = []
	additional_similarities = []
	for i in range(len(links)):
		link_with_thumbnail = links[i].split(",")
		link_this = link_with_thumbnail[0]
		link_thumb = link_with_thumbnail[1]
		isYandere = isYandereLink(link_this)
		isDanbooru = isDanbooruLink(link_this)
		if (isYandere | isDanbooru):
			thread = threading.Thread(target = findPixivInfoExternal, args = [link_this, additional_links, link_thumb, additional_similarities, similarities[i]])
			thread.start()
			threads.append(thread)
	for thread in threads:
		thread.join()
	threads.clear()

	links = [*additional_links, *links]
	similarities = [*additional_similarities, *similarities]
	responses = [False] * len(links)
	for i in range(len(links)):
		link_with_thumbnail = links[i].split(",")
		link_this = link_with_thumbnail[0]
		# link_thumb = link_with_thumbnail[1]
		pid = isPixivLink(link_this)
		if (pid):
			pixiv_check_valid_url = f"https://pixiv.cat/{pid}.jpg"
			thread = threading.Thread(target = urlIsImage, args = [pixiv_check_valid_url, responses, i])
			thread.start()
			threads.append(thread)
			pixiv_check_valid_url = f"https://pixiv.cat/{pid}-1.jpg"
			thread = threading.Thread(target = urlIsImage, args = [pixiv_check_valid_url, responses, i])
			thread.start()
			threads.append(thread)
		else:
			responses[i] = True
	for thread in threads:
		thread.join()
	for index, response in reversed(list(enumerate(responses))):
		if (not response):
			links.pop(index)
			similarities.pop(index)

	try:
		yandex_url = generateYandexURL(image_path)
	except Exception as e:
		yandex_url = "yandex_error"
		print("[Error] Yandex bot detected.")
	links.append(yandex_url)

	keyboard = [
		[
			InlineKeyboardButton("⭕", callback_data = "correct"),
			InlineKeyboardButton("❌", callback_data = "wrong"),

		],
		[
			InlineKeyboardButton("この画像で検索する", callback_data = "retry"),
		],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)
	current_link = links[0].split(",")[0]

	sent_message = context.bot.send_message(chat_id = update.effective_chat.id, text = f"類似度:{similarities[0]} {current_link}", reply_markup = reply_markup)
	print(f"[{log_user}] Search result {similarities[0]} {current_link} sent.")

	with open(os.path.join("data", f"{sent_message.chat.id}_{sent_message.message_id}.txt"), "w") as f:
		f.write("0\n")
		for similarity in similarities:
			f.write(f"{similarity} ")
		f.write('\n')
		for link in links:
			f.write(f"{link}\n")

def callback(update: Update, context: CallbackContext):
	keyboard = [
		[
			InlineKeyboardButton("⭕", callback_data = "correct"),
			InlineKeyboardButton("❌", callback_data = "wrong"),

		],
		[
			InlineKeyboardButton("この画像で検索する", callback_data = "retry"),
		],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)

	query = update.callback_query
	log_user = logUser(query.message)
	query_history_path = os.path.join("data", f"{query.message.chat.id}_{query.message.message_id}.txt")
	print(f"[{log_user}] Pressed {query.data}.")
	if (not os.path.exists(query_history_path)):
		query.answer()
		try:
			query.edit_message_text(text = update.callback_query.message.text)
		except BadRequest:
			pass
		print(f"[{log_user}] Buttons expired.")
		return
	if (query.data == "wrong"):
		with open(query_history_path, "r") as f:
			links = f.readlines()

		head_ptr = int(links[0])
		similarities = links[1].split(" ")
		links_log = links.copy()
		for i in range((head_ptr + 3), len(links)):
			links[i] = links[i].split(",")[0]
		if (head_ptr + 4 >= len(links)):
			
			keyboard = [
				[
					InlineKeyboardButton("Yandex", url = links[-1]),

				],
			]
			if (links[-1] == "yandex_error"):
				keyboard = []
			reply_markup = InlineKeyboardMarkup(keyboard)
			query.answer()
			try:
				query.edit_message_text(text = "もう限界だ🥺", reply_markup = reply_markup)
			except BadRequest:
				pass
			print(f"[{log_user}] Yandex url returned.")
			if (os.path.isfile(query_history_path)):
				os.remove(query_history_path)
			return
		head_ptr += 1
		query.answer()
		try:
			query.edit_message_text(text = f"類似度:{similarities[head_ptr]} {links[head_ptr + 2]}", reply_markup = reply_markup)
		except BadRequest:
			pass
		print(f"[{log_user}] Search result {similarities[head_ptr]} {links[head_ptr + 2]} sent.")

		with open(query_history_path, "w") as f:
			f.write(f"{head_ptr}\n")
			for i in range(1, len(links_log)):
				f.write(f"{links_log[i]}")

	elif (query.data == "retry"):
		with open(query_history_path, "r") as f:
			links = f.readlines()

		head_ptr = int(links[0])
		retry_link = links[head_ptr + 2].split(",")[1].rstrip("\n")
		yandex_url = links[-1].rstrip("\n")
		print(f"[{log_user}] Retry search link {retry_link}.")

		try:
			links, similarities = saucenaoSearch(retry_link)
		except Exception as e:
			query.answer()
			print(f"[{log_user}] Saucenao error {e}.")

		links.append(yandex_url)

		with open(os.path.join("data", f"{query.message.chat.id}_{query.message.message_id}.txt"), "w") as f:
			f.write("0\n")
			for similarity in similarities:
				f.write(f"{similarity} ")
			f.write('\n')
			for link in links:
				f.write(f"{link}\n")

		current_link = links[0].split(",")[0]

		query.answer()
		try:
			query.edit_message_text(text = f"類似度:{similarities[0]} {current_link}", reply_markup = reply_markup)
		except BadRequest:
			pass
		print(f"[{log_user}] Search result {similarities[0]} {current_link} sent.")

	elif (query.data == "correct"):
		query.answer()
		try:
			query.edit_message_text(text = update.callback_query.message.text)
		except BadRequest:
			pass
		print(f"[{log_user}] Search ended.")
		if (os.path.isfile(query_history_path)):
				os.remove(query_history_path)
