"""
Get bible verses by bible website scraping.
>>  'http://www.bskorea.or.kr'  <<
Utilize `requests` and `BeautifulSoup` to scrap website.
"""

import re
from typing import List

from requests import get
from bs4 import BeautifulSoup
from bs4.element import ResultSet


class Bible:
    """Bible class"""

    def __init__(
        self,
        book: str,
        chapter: int,
        phrase: int,
        version: str,
    ):
        self._book: str = book
        self._chapter: str = chapter
        self._phrase: int = phrase
        self._version: str = version

    @property
    def book(self):
        """Property: `book`"""
        return self._book

    @book.setter
    def book(self, value: str):
        self._book = value

    @property
    def chapter(self):
        """Property: `chapter`"""
        return self._chapter

    @chapter.setter
    def chapter(self, value: int):
        self._chapter = value

    @property
    def phrase(self):
        """Property: `phrase`"""
        return self._phrase

    @phrase.setter
    def phrase(self, value: int):
        self._section = value

    @property
    def version(self):
        """Property: `version`"""
        return self._version

    @version.setter
    def version(self, value: str):
        self._version = value


class BibleScraper:
    """
    Scrap bible website.

    args:
        bible: Bible | List[Bible]

    methods:
        get_bible: callable
    """

    def __init__(
        self,
        bible: Bible | List[Bible],
    ) -> None:

        if bible is not list:  # For one phrase
            self.get_bible: callable = self.__get_one_phrase

        elif bible is list:  # For multiple phrases
            self.get_bible: callable = self.__get_phrases

        else:  # Invalid `bible` input
            raise ValueError("Invalid bible input")

        self.bible = bible

    def __get_one_phrase_html(self) -> ResultSet:
        """Get bible phrase HTML"""

        url = (
            "http://www.bskorea.or.kr/bible/korbibReadpage.php?"
            f"version={self.bible.version}&"
            f"book={self.bible.book}&"
            f"chap={self.bible.chapter}&"
            f"phrase={self.bible.phrase}&"
            "cVersion=&fontSize=15px&fontWeight=normal"
        )

        response = get(url=url, timeout=10)

        if response.status_code != 200:  # If you cannot get response
            raise LookupError("Cannot get response from website")

        html_parser = BeautifulSoup(response.text, "html.parser")
        html_lines = html_parser.find_all("span", class_="")

        removes_div = html_parser.find_all("div", class_="D2")
        for remove in removes_div:
            remove.decompose()

        removes_a = html_parser.find_all("a", class_="comment")
        for remove in removes_a:
            remove.decompose()

        return html_lines

    def __get_one_phrase_text(
        self,
        html_lines: str,
        bible: Bible,
    ) -> str:
        for line in html_lines:
            digits = re.sub(r"[^0-9]", "", line.text)

            if bible.phrase == int(digits):
                phrase_text = str.strip(line.text[len(digits) :])  # Phrase of section

                return phrase_text

    def __get_one_phrase(
        self,
        bible: Bible,
    ) -> str:
        """Get one bible phrase"""

        html = self.__get_one_phrase_html()
        text = self.__get_one_phrase_text(html_lines=html, bible=bible)

        return text

    def __get_phrases(self):
        """Get multiple bible phrases at once"""

    # TODO: Implement get_phrases method; get multiple phrases at once
