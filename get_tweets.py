import requests, textwrap
import webbrowser
import emoji
from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu
import re

class TweetObject():
	"""Contains all necessary parameters to store for each tweet"""
	link = ""
	author = ""
	handle = ""
	body_text = ""
	date = ""
	links = []

	#
	#


	def __init__(self, blockquote):
		self.body_text = blockquote.p.text.replace("|", ";")
		self.get_date_from_tweet(blockquote)
		self.get_author_from_tweet(blockquote)
		self.get_links_from_tweet(blockquote)

	def get_links_from_tweet(self, blockquote):
		templinks = blockquote.p.find_all('a')
		templist = []
		for link in templinks:
			if "t.co" in link.text:
				templist.append(link.text)
		self.links = templist


	def get_date_from_tweet(self, blockquote):
		""" once you"ve extracted all block quotes from the page as objects,
		pass them here. The last link is always the date value (and the direct
		link to the tweet)
		"""

		temp = blockquote.find_all('a')
		date_link = temp[len(temp)-1]
		self.link = date_link.get("href")
		self.date = date_link.text

	def get_author_from_tweet(self, blockquote):
		start = blockquote.text.index("— ") + 2
		end = blockquote.text.index("(@")
		handle_end = blockquote.text.index(") ", end)
		self.author = blockquote.text[start:end].replace("|", ";")
		self.handle = blockquote.text[end:handle_end].replace("(", "").replace(")", "")

	def print_tweet(self):
		print(f"Date: {self.date}")
		print(f"Author: {self.author} ({self.handle})")
		print(self.body_text)

def print_body(body_text):
	temp = body_text.split("[]")
	if len(temp) > 1:
		return(textwrap.fill(temp[0]) + "\n" + temp[1])
	else:
		return(textwrap.fill(temp[0]))

def deEmojify(text):
	return emoji.get_emoji_regexp().sub(r'', text)

def main():
	url = "http://www.asptweets.com"

	page = requests.get(url)

	soup = BeautifulSoup(page.text, 'html.parser')

	page_options = soup.find_all(class_='dropdown-item')[:11]
	page_titles = []
	page_urls = []
	url_count = "a"
	for option in page_options:
		page_titles.append(f"[{url_count}] {option.text}")
		page_urls.append(option.get('href'))
		url_count = chr(ord(url_count) + 1)

	terminal_menu = TerminalMenu(page_titles, title="Select date to view Tweets from:", clear_screen=True)
	selected_page = terminal_menu.show()

	url = url + page_urls[selected_page]

	page = requests.get(url)

	soup = BeautifulSoup(page.text, 'html.parser')

	blockquotes = soup.find_all('blockquote')

	tweets = []
	menu_list = []
	count = 1

	for blockquote in blockquotes:
		temp = TweetObject(blockquote)
		tweets.append(temp)
		menu_list.append(f"{deEmojify(temp.author)} ({temp.handle})|{temp.body_text}[]{temp.link}")
		count += 1

	terminal_menu = TerminalMenu(menu_list, preview_command=print_body, preview_size=0.50, title=page_titles[selected_page], multi_select=True, show_multi_select_hint=True, clear_screen=True)
	menu_entry_index = terminal_menu.show()

	for item in menu_entry_index:
		for link in tweets[item].links:
			webbrowser.open(link, new=2)

if __name__ == '__main__':
	main()


