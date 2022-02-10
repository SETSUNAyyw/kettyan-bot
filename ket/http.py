from bs4 import BeautifulSoup
from requests.exceptions import Timeout, SSLError
import requests
import os
import re
import threading
import urllib.parse
import json

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

def urlIsImage(url, responses = None, index = 0):
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
	if (not responses):
		return valid_pid, url_compressed
	elif (valid_pid):
		responses[index] = valid_pid

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

def saucenaoSearch(image_path):
	search_results = []
	similarities = []
	if ("saucenao" in image_path):
		try:
			image_path = image_path.replace("db=-3", "dbs[]=5&dbs[]=8&dbs[]=9&dbs[]=12&dbs[]=21&dbs[]=25&dbs[]=28&dbs[]=35&dbs[]=41")
			if (os.path.exists("token_sauce.txt")):
				with open("token_sauce.txt", "r") as f:
					token = f.readline()
				image_path += f"&api_key={token}"
			response = requests.get(url = image_path, timeout = (3.0, 10.0))
		except (SSLError, Timeout) as e:
			raise e
	else:
		try:
			with open(image_path, "rb") as file_object:
				files = {'file': file_object.read()}
		except Exception as e:
			raise e
		url = "https://saucenao.com/search.php"
		params = (
			("dbs[]", 5),
			("dbs[]", 8),
			("dbs[]", 9),
			("dbs[]", 12),
			("dbs[]", 21),
			("dbs[]", 25),
			("dbs[]", 28),
			("dbs[]", 35),
			("dbs[]", 41),
		)
		try:
			response = requests.post(url = url, files = files, params = params, timeout = (3.0, 10.0))
		except (SSLError, Timeout) as e:
			raise e
	soup = BeautifulSoup(response.content, "html.parser")
	results = soup.find_all("div", class_ = "result")
	for result in results:
		links = result.find_all("a")
		similarity = result.find("div", class_ = "resultsimilarityinfo")
		redirect = result.find("a", class_ = "linkify")
		for link in links:
			href = link.get("href")
			if (href):
				if (not "saucenao" in href):
					search_results.append(href + "," + redirect.get("href"))
					break
		if (similarity):
			similarities.append(similarity.text)
		else:
			similarities.append("Unknown")
	return search_results, similarities

def generateYandexURL(image_path):
	url = "https://yandex.ru/images/search"
	files = {"upfile": ("blob", open(image_path, "rb"), "image/jpeg")}
	params = {
		"rpt": "imageview",
		"format": "json",
		"request": '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'
	}
	response = requests.post(url = url, files = files, params = params)
	try:
		query_string = json.loads(response.content)["blocks"][0]["params"]["url"]
	except Exception as e:
		raise e
	yandex_url = url + "?" + query_string
	return yandex_url

def isPixivLink(url):
	pid = re.findall(r"https://www.pixiv.net/(artworks/|(.*illust_id=))(\d+)", url)
	if (pid):
		return pid[0][2]
	else:
		return None

def isYandereLink(url):
	isYandere = re.findall(r"https://yande.re/post/show/(\d+)", url)
	if (isYandere):
		return True
	else:
		return False

def isDanbooruLink(url):
	isDanbooru = re.findall(r"https://danbooru.donmai.us/post/show/(\d+)", url)
	if (isDanbooru):
		return True
	else:
		return False

def findPixivInfoExternal(url, additional_links = None, link_thumb = None, additional_similarities = None, similarity = None):
	try:
		html = requests.get(url, timeout = (3.0, 3.0))
	except Timeout as e:
		if (not link_thumb):
			raise e
		else:
			pass
	soup = BeautifulSoup(html.content, "html.parser")
	pid = re.findall(r"https://www.pixiv.net/(artworks/|(.*illust_id=))(\d+)", str(soup))
	if (pid):
		if (link_thumb):
			additional_links.append(f"https://www.pixiv.net/artworks/{pid[0][2]},{link_thumb}")
			additional_similarities.append(similarity)
		else:
			return pid[0][2]
	else:
		if (not link_thumb):
			return None
		else:
			pass
