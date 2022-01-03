from bs4 import BeautifulSoup
from requests.exceptions import Timeout, SSLError
import requests
import os
import re
import threading

def downloadImage(urls, pids, pages):
	if (isinstance(urls, str)):
		urls = [urls]
	if (isinstance(pids, str)):
		pids = [pids]
	if (isinstance(pages, int)):
		pages = [pages]
	paths = []
	threads = []
	for page, url, pid in zip(pages, urls, pids):
		filename = pid
		if (page > 0):
			filename += ("-" + str(page))
		filename += ".jpg"
		path = os.path.join("img", filename)
		try:
			thread = threading.Thread(target = downloadImageHelper, args = [url, path])
			thread.start()
			threads.append(thread)
		except (SSLError, Timeout) as e:
			pass
		paths.append(path)
	for thread in threads:
		thread.join()
	for path in paths:
		if (not os.path.exists(path)):
			paths.remove(path)
	if (not paths):
		raise Exception
	if (len(paths) == 1):
		return paths[0]
	else:
		return paths

def downloadImageHelper(url, path):
	if (not os.path.exists(path)):
		try:
			html = requests.get(url, timeout = (3.0, 30.0))
		except (SSLError, Timeout) as e:
			raise e
		with open(path, "wb") as f:
			f.write(html.content)

def urlEdit(url):
	url = url.replace("pximg.net", "pixiv.cat")
	url = url.replace("original", "master")
	url = url.rstrip(".png")
	url = url.rstrip(".jpg")
	url += "_master1200.jpg"
	return url

def urlIsImage(url):
	try:
		html = requests.head(url, timeout = (3.0, 3.0))
	except (SSLError, Timeout) as e:
		raise e
	html_dic = eval(str(html.headers).lower())
	valid_pid = ((html_dic["content-type"] == "image/jpeg") 
			| (html_dic["content-type"] == "image/png"))
	try:
		url_compressed = urlEdit(html_dic["x-origin-url"])
	except KeyError:
		url_compressed = None
	return valid_pid, url_compressed

def crawlPixivInfo(pid):
	demo_url = "https://www.pixiv.net/artworks/" + pid
	try:
		html = requests.get(demo_url, timeout = (3.0, 3.0))
	except Timeout as e:
		raise e
	soup = BeautifulSoup(html.content, "html.parser")
	r_18 = re.findall(r"\"tag\":\"R-18\"", str(soup))
	soup = soup.find("title")
	demo_caption = re.findall(r"<title>(.*?)<\/title>", str(soup))[0]
	demo_caption = "<a href='{}'>{}</a>".format(demo_url, demo_caption)
	if (r_18):
			demo_caption = "<a> #NSFW </a>" + demo_caption
	return demo_caption

def fetchLolicon(num = 1, r_18 = False, args = None, keyword = None):
	url = "https://api.lolicon.app/setu/v2?size=regular&num={}".format(num)
	if (r_18):
		url += "&r18=1"
	if (args):
		for tag in args:
			if (tag.lower() == "r18"):
				tag = "R-18"
			url += ("&tag=" + tag)
	if (keyword):
		url += ("&keyword=" + keyword)
	try:
		html = requests.get(url, timeout = (3.0, 3.0))
	except Timeout as e:
		raise e
	soup = BeautifulSoup(html.content, "html.parser")
	soup = eval(str(soup).replace("false", "False").replace("true", "True"))
	data = soup["data"]
	if (data):
		infos = [[str(data[i]["pid"]), data[i]["p"], data[i]["urls"]["regular"]] for i in range(num)]
	else:
		infos = []
	return infos
