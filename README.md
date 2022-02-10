# kettyan-bot

This bot can search or randomly fetch pictures from [Pixiv](https://www.pixiv.net/).

## Usage

- To use the bot, send `/start` or `/help` to [けっちゃん](https://t.me/kettyan_bot).
- For full usage documentation (supported in English/日本語/中文), click [here](https://remisiki.github.io/kettyan-bot/).
- To build from source code, first install `requirements.txt` using pip3:

	```bash
	pip install -r requirements.txt
	```

	Then run with Python3:

	```bash
	python main.py
	``` 

	`token.txt` should be put under the root directory, which contains your [access token key of telegram bot](https://core.telegram.org/bots#6-botfather).

	`token_sauce.txt` should also be included under the root directory, which contains your access key of [Saucenao](https://saucenao.com/user.php?page=search-api). If you don't have one, you may just ignore this but certain searching patterns may be prohibited.

	**P.S. You should never give your access token keys to anyone else.**

## API

- [Python Telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [lolicon](https://api.lolicon.app/#/setu)
- [pixiv.cat](https://pixiv.cat/)
- [Saucenao](https://saucenao.com/)