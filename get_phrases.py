from requests import get
from bs4 import BeautifulSoup
import re
import json


class getPhrases:
    def __init__(self,
                 ):

        # Dictionary loading...
        with open("dict/version-dict.json", "r") as ver_json:
            self.version_dict = json.load(ver_json)  # version in Kr -> version in En
        with open("dict/book-dict.json", "r") as book_json:
            self.book_dict = json.load(book_json)    # book in Kr -> book in En

    # By book, chapter and section, 'get URL'
    def _get_url(self,
                 version: str,
                 book: str,
                 chap: int,
                 sec: int,
                 ):

        # Set version, book, chapter of bible
        version = self.version_dict[version]
        book = self.book_dict[book]
        chap = chap
        self.sec = sec

        # URL segments with version, book, chapter and the rest
        url_0 = "http://www.bskorea.or.kr/bible/korbibReadpage.php?"
        url_1 = f"version={version}&"
        url_2 = f"book={book}&"
        url_3 = f"chap={chap}&"
        url_4 = f"sec={sec}&"
        url_5 = "cVersion=&fontSize=15px&fontWeight=normal"

        # Form a complete URL with URL segments
        base_url = url_0 + url_1 + url_2 + url_3 + url_4 + url_5

        return base_url

    def get_phrase(self,
                   version: str,
                   book: str,
                   chap: int,
                   sec: int,
                   ):

        base_url = self._get_url(version, book, chap, sec)

        # Get response from URL
        response = get(f"{base_url}")

        if response.status_code != 200:     # If we cannot scrap website
            print("Can't request website")

        else:                               # If we can scrap website
            # Get html with BeautifulSoup lib.
            soup = BeautifulSoup(response.text, "html.parser")

            # Find phrases in html
            lines = soup.find_all("span", class_="")

            removes_div = soup.find_all("div", class_="D2")
            for remove in removes_div:
                remove.decompose()

            removes_a = soup.find_all("a", class_="comment")
            for remove in removes_a:
                remove.decompose()

            for line in lines:
                digits = re.sub(r"[^0-9]", "", line.text)
                if self.sec == int(digits):            # Number of section
                    return str.strip(line.text[len(digits):])     # Phrase of section
