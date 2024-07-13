"""Main code"""

from src.bible import Bible, BibleScraper
from src.lyrics import Song, LyricsScraper, SaveLyrics

ls = LyricsScraper(song_title="주의 사랑으로")
song = ls.get_song()

sl = SaveLyrics(song_class=song)
sl.save_lyrics()
