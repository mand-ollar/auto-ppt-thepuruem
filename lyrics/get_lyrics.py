from requests import get
from bs4 import BeautifulSoup
from pathlib import Path

import re
import json

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
        self.pth = Path.cwd()
    
    def __part_separation_to_json__(self,
                                    file: Path,
                                    title: str,
                                    ):
        # read txt file
        with open(file, "r") as f:
            lyrics_txt = f.read()
            f.close()
        
        # remove all characters except alphabets and numbers(for A, B, A1, A2, ...)
        lyrics_parts = re.sub(r"[^a-dA-D0-9Z]", "", lyrics_txt)

        # find alphabets idx
        alph_idx = []
        for i in range(len(lyrics_parts)):
            if lyrics_parts[i].isalpha():
                alph_idx.append(i)
        alph_idx.append(len(lyrics_parts))
        
        # part segments list
        temp = []
        for i in range(len(alph_idx)-1):
            temp.append(lyrics_parts[alph_idx[i]:alph_idx[i+1]])
        lyrics_parts = temp
        
        # part segments idx from txt file
        idx = []
        for parts in lyrics_parts:
            idx.append(lyrics_txt.find(parts))
        idx.append(len(lyrics_txt))
        
        # make lyrics dict by parts {A: str, B: str, ...}
        output = {}
        for i in range(len(lyrics_parts)):
            text = lyrics_txt[idx[i]+len(lyrics_parts[i]):idx[i+1]]
            output[lyrics_parts[i]] = text.strip()
        
        # write json file
        with open(f"lyrics/json/{title}.json", "w", encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii = False)
            f.close()

    def __txt_to_json(self,
                      song_title: str,
                      ):
        txt_folder = self.pth/"lyrics/txt"
        file_list = list(txt_folder.glob("*.txt"))
        
        for file in file_list:
            file_str = str(file)
            
            idxl = file_str.rfind("/")
            idxr = file_str.rfind(".")
            title = file_str[idxl+1:idxr]
            
            if song_title.replace(" ", "") in title.replace(" ", ""):
                self.__part_separation_to_json__(file, title)
                print("Json conversion complete")
                return -1
        
        print(f"No txt file named {song_title} found.")

    def __save_as_txt__(self,
                        song_title: str,
                        lyrics: str,
                        ):
        if not Path(f"lyrics/txt/{song_title}.txt").exists():
            with open(f"lyrics/txt/{song_title}.txt", "w") as lyrics_txt:
                lyrics_txt.write(lyrics)
                lyrics_txt.close()
        
        if not self.__is_fit_style__(f"lyrics/txt/{song_title}.txt"):
            print(f"Go to lyrics/txt/{song_title}.txt and set the lyrics part manually.")

    def __is_fit_style__(self,
                         file: str,
                         ):
        with open(file, "r") as f:
            text = f.read()
            f.close()
        
        is_fit = True
        
        # check if there are some alphabets
        if "A" not in text:
            is_fit = False
        
        segments = text.split("\n")
        for segment in segments:
            if len(segment) > 20:
                is_fit = False
                break
        
        if not is_fit:
            print(f"Cannot make it to json because the style is wrong. Check [{file}] again.")
            return False
        else:
            return True

    def get_lyrics(self,
                   song_title: str,
                   artist_name=""
                   ):
        
        # Check if lyrics json file exists
        json_folder = self.pth/"lyrics/json"
        file_list = list(json_folder.glob("*.json"))

        for file in file_list:
            file_str = str(file)
            
            idxl = file_str.rfind("/")
            idxr = file_str.rfind(".")
            title = file_str[idxl+1:idxr]

            if song_title.replace(" ", "") in title.replace(" ", ""):
                print("Lyrics json file exists in [/lyrics/json] folder.")
                
                return -1
        
        # Check if lyrics txt file exists when json file does not exist
        txt_folder = self.pth/"lyrics/txt"
        file_list = list(txt_folder.glob("*.txt"))
        
        for file in file_list:
            file_str = str(file)
            
            idxl = file_str.rfind("/")
            idxr = file_str.rfind(".")
            title = file_str[idxl+1:idxr]
            
            if song_title.strip() in title.strip():
                print("Lyrics txt file exists in [/lyrics/txt] folder.")
                is_fit = self.__is_fit_style__(file)
                
                # End function if lyrics txt file is not fit
                if not is_fit:
                    return -1
                else:
                    print("Converting to json file...")
                    self.__txt_to_json(title)
                    return -1
        
        song_title = song_title.replace(" ", "+")

        url_0 = "https://www.melon.com/search/total/index.htm?q="
        url_1 = song_title
        url_2 = "&section=&mwkLogType=T"
        url = url_0 + url_1 + url_2

        response = get(url, headers={"User-Agent": "XY"})
        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.find_all("a", title="곡정보 보기")
        artists = soup.find_all("a", class_="fc_mgray")
        
        lyrics = []
        while lyrics == []:
            # if artist_name is not given
            if artist_name == "":
                i = 0
                print("[NO ARTIST NAME ENTERED]\n")
                for i in range(5):
                    k = i * 3
                    print(f"{i + 1}] {artists[k].text}")
                print()
                artist_name = artists[3 * int(input("Choose the artist: ")) - 2].text
                print()
                
            for artist in artists:
                if artist_name in artist.text:
                    idx = artists.index(artist)
                    break
                
                # if there's no matched artist
                print(f"Cannot find {artist_name}!\n")
                artist_name = ""
                break
            if artist_name == "":
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
        self.__save_as_txt__(song_title, lyrics)

# TODO: song part separation

if __name__ == "__main__":
    getLyrics = getLyrics()
    getLyrics.get_lyrics(song_title="당신의 날에", artist_name="WELOVE")
