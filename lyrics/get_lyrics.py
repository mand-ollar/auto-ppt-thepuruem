from requests import get
from bs4 import BeautifulSoup
from pathlib import Path

import re
import json
import unicodedata
import os

'''
ARTIST NAMES SHOULD INCLUDE:

마커스
WELOVE
제이어스
어노인팅
아이자야
'''

class getLyrics:
    def __init__(self,
                 ):
        self.pth = Path(__file__).parent.parent

    def _print(self,
               x,
               ):
        print(x) if self.print_it else None

    def _part_separation_to_json_(self,
                                  file: Path,
                                  title: str,
                                  ):
        # read txt file
        with open(file, "r") as f:
            lyrics_txt = f.read().split("\n")
            f.close()

        # get part segments
        lyrics_parts = []
        for lyric in lyrics_txt:
            if len(lyric) == 2 and lyric[1].isdigit():
                lyrics_parts.append(lyric)
            elif len(lyric) == 1:
                lyrics_parts.append(lyric)

        # part segments idx from txt file
        idx = []
        for parts in lyrics_parts:
            idx.append(lyrics_txt.index(parts))
        idx.append(len(lyrics_txt))

        # make lyrics dict by parts {A: str, B: str, ...}
        output = {}
        for i in range(len(lyrics_parts)):
            text = "\n".join(lyrics_txt[idx[i]+1:idx[i+1]])
            output[lyrics_parts[i]] = text.strip()

        # write json file
        with open(f"lyrics/json/{title}.json", "w", encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii = False)
            f.close()

    def _txt_to_json_(self,
                      song_title: str,
                      ):
        txt_folder = self.pth/"lyrics/txt"
        file_list = list(txt_folder.glob("*.txt"))

        def trans(x):
            return unicodedata.normalize('NFC', x)

        for file in file_list:
            title = trans(file.stem)

            if title == song_title:
                self._part_separation_to_json_(file, title)
                print("Json conversion complete")
                print()
                return False

        self._print(f"No txt file named {song_title} found.")

    def _save_as_txt_(self,
                      song_title: str,
                      lyrics: str,
                      ):
        if not Path(f"lyrics/txt/{song_title}.txt").exists():
            with open(f"lyrics/txt/{song_title}.txt", "w") as lyrics_txt:
                lyrics_txt.write(lyrics)
                lyrics_txt.close()

        if not self._is_fit_style_(f"lyrics/txt/{song_title}.txt"):
            self._print(f"Go to lyrics/txt/{song_title}.txt and set the lyrics part manually.")

    def _is_fit_style_(self,
                       file: str,
                       ):
        with open(file, "r") as f:
            text_segments = f.read().split("\n")
            f.close()

        is_fit = True

        def check_idx_exitsts(segment: str,
                              ):
            if len(segment) == 1:
                return True
            elif len(segment) == 2 and segment[1].isdigit():
                return True
            else:
                return False

        idx_exists = False
        for segment in text_segments:
            if len(segment) > 24:
                is_fit = False
                break
            if not idx_exists and check_idx_exitsts(segment):
                idx_exists = True
        if not idx_exists:
            is_fit = False

        if not is_fit:
            self._print(f"Cannot make it to json because the style is wrong. Check [{file}] again.")
            return False
        else:
            return True

    def get_lyrics(self,
                   song_title: str,
                   artist_name="thisisnotanartistname",
                   print_it: bool = True,
                   ):
        self.print_it = print_it

        # Check if lyrics json file exists
        json_folder = self.pth/"lyrics/json"
        file_list = list(json_folder.glob("*.json"))

        for file in file_list:
            def trans(x):
                return unicodedata.normalize('NFC', x)

            title = trans(file.stem)

            if song_title.replace(" ", "") in title.replace(" ", ""):
                self._print(f"Lyrics json file [{song_title}.json] exists in [/lyrics/json] folder.\n")

                return False

        # Check if lyrics txt file exists when json file does not exist
        txt_folder = self.pth/"lyrics/txt"
        file_list = list(txt_folder.glob("*.txt"))

        for file in file_list:
            def trans(x):
                return unicodedata.normalize('NFC', x)

            title = trans(file.stem)
            
            if song_title.strip() in title.strip():
                self._print("Lyrics txt file exists in [/lyrics/txt] folder.")
                is_fit = self._is_fit_style_(file)
                
                # End function if lyrics txt file is not fit
                if not is_fit:
                    return True
                else:
                    print("Converting to json file...")
                    self._txt_to_json_(title)
                    return False

        song_title = song_title.replace(" ", "+")

        url_0 = "https://www.melon.com/search/total/index.htm?q="
        url_1 = song_title
        url_2 = "&section=&mwkLogType=T"
        url = url_0 + url_1 + url_2

        response = get(url, headers={"User-Agent": "XY"})
        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.find_all("a", title="곡정보 보기")
        artists = soup.find_all("div", id="artistName")

        lyrics = []
        while lyrics == []:
            # if artist_name is not given
            if artist_name == "thisisnotanartistname":
                i = 0
                print(f"Search results for {song_title.replace('+', ' ')}...")
                print()
                print("[NO ARTIST NAME ENTERED]\n")
                print(len(artists))
                for i in range(min(5, len(artists))):
                    k = i
                    print(f"{i + 1}] {artists[k].a.text}") if artists[k].a != None else print(f"{i + 1}] ")
                print()
                artist_name = artists[int(input("Choose the artist: ")) - 1].a.text
                print()

            not_broken = True
            for artist in artists:
                # if there's a matched artist
                if artist_name in artist.a.text:
                    idx = artists.index(artist)
                    not_broken = False
                    break

            if not_broken:
                # if there's no matched artist
                print(f"Cannot find {artist_name}!\n")
                artist_name = "thisisnotanartistname"
                if artist_name == "thisisnotanartistname":
                    continue

            text = titles[idx//3]["href"]
            song_id = text[text.rfind("(")+2:-3]

            song_url_0 = "https://www.melon.com/song/detail.htm?songId="
            song_url_1 = song_id
            song_url = song_url_0 + song_url_1

            response = get(song_url, headers={"User-Agent": "XY"})
            soup = BeautifulSoup(response.text, "html.parser")
            lyrics = soup.find_all("div", class_="lyric")
            
            if lyrics == []:
                artist_name = ""
                print("[NO LYRICS FOUND]")

        remove_0 = '<div class="lyric" id="d_video_summary"><!-- height:auto; 로 변경시, 확장됨 -->'
        remove_1 = '</div>'
        remove_2 = '<br/>'

        lyrics = str(lyrics[0]).replace(remove_0, "")
        lyrics = lyrics.replace(remove_1, "")
        lyrics = lyrics.replace(remove_2, "\n")
        lyrics = str.strip(lyrics)

        song_title = song_title.replace("+", " ")
        self._save_as_txt_(song_title, lyrics)

        return False

# TODO: song part "auto" separation

if __name__ == "__main__":
    getLyrics = getLyrics()
    title = "주만 바라볼찌라"
    getLyrics.get_lyrics(song_title=title, artist_name="소리엘")#thisisnotanartistname")
