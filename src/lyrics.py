"""
Get song lyrics from Melon.
>>  'https://www.melon.com'  <<
Utilize `requests` and `BeautifulSoup` to scrap website.
"""

# Internal
import re
import json
import random
import string
import subprocess
from copy import copy
from pathlib import Path
from typing import List, Union, Tuple, Dict, Literal

# External
from requests import get
from bs4 import BeautifulSoup
from bs4.element import ResultSet

# Project
from utils.selection import select_option


class Song:
    """Song class"""

    def __init__(self):
        self._title: str | None = None
        self._song_id: str | None = None
        self._artist: str | None = None
        self._lyrics_txt: str | None = None
        self._lyrics_dict: dict | None = None

    @property
    def title(self):
        """Property: `title`"""
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def song_id(self):
        """Property: `song_id`"""
        return self._song_id

    @song_id.setter
    def song_id(self, value: str):
        self._song_id = value

    @property
    def artist(self):
        """Property: `artist`"""
        return self._artist

    @artist.setter
    def artist(self, value: str):
        self._artist = value

    @property
    def lyrics_txt(self):
        """Property: `lyrics_txt`"""
        return self._lyrics_txt

    @lyrics_txt.setter
    def lyrics_txt(self, value: str):
        self._lyrics_txt = value

    @property
    def lyrics_dict(self):
        """Property: `lyrics_dict`"""
        return self._lyrics_dict

    @lyrics_dict.setter
    def lyrics_dict(self, value: dict):
        self._lyrics_dict = value


class LyricsScraper:
    """
    Scrap lyrics from Melon.

    args:
        song_title: str

    methods:
        get_song: Get Song class with lyrics
    """

    def __init__(
        self,
        song_title: str,
    ):
        self.song_title = song_title

    def __get_search_html(
        self,
    ) -> ResultSet:
        """Get lyrics html"""

        # For url, space has to be replaced with '+'
        url_formatted_song_title = self.song_title.replace(" ", "+")

        search_url = (
            "https://www.melon.com/search/total/index.htm?q="
            f"{url_formatted_song_title}"
            "&section=&mwkLogType=T"
        )

        response = get(search_url, timeout=10, headers={"User-Agent": "XY"})
        html_parser = BeautifulSoup(response.text, "html.parser")

        return html_parser

    def __get_search_artists_result(
        self,
        html_parser: BeautifulSoup,
        max_results: int = 5,
    ) -> List[Union[str, None]]:
        """Get lyrics artists list"""

        artists_resultset = html_parser.find_all("div", id="artistName")

        artists_list = []
        for artist_resultset in artists_resultset:
            if len(artists_list) == max_results:
                break

            artists_list.append(
                artist_resultset.a.text if artist_resultset.a is not None else None
            )

        return artists_list

    def __get_search_titles_result(
        self,
        html_parser: BeautifulSoup,
        max_results: int = 5,
    ) -> Tuple[List[Union[str, None]]]:
        """Get lyrics titles list"""

        titles_resultset = html_parser.find_all("a", title="곡정보 보기")

        titles_list = []
        song_ids_list = []
        for title_resultset in titles_resultset:
            if len(titles_list) == max_results:
                break

            titles_list.append(
                title_resultset.text.split(" 상세정보 페이지 이동")[0]
                if title_resultset is not None
                else None
            )

            # From "melon.link.goSongDetail('36879099');", extract id "36879099"
            match = re.search(
                pattern=r"melon\.link\.goSongDetail\('(\d+)'\)",
                string=title_resultset["href"],
            )
            song_ids_list.append(
                match.group(1) if match else ValueError("Cannot find song id")
            )

        return titles_list, song_ids_list

    def _get_search(
        self,
    ) -> Dict[Literal["keyword", "artist", "song_id", "title"], List[str | None]]:
        search_html = self.__get_search_html()
        artists = self.__get_search_artists_result(html_parser=search_html)
        titles, song_ids = self.__get_search_titles_result(html_parser=search_html)

        output_dict = {
            "keyword": self.song_title,
            "artist": artists,
            "song_id": song_ids,
            "title": titles,
        }

        return output_dict

    def __select_song(
        self,
        search_results: Dict[
            Literal["keyword", "artist", "song_id", "title"], List[str | None]
        ],
    ) -> Dict[Literal["keyword", "artist", "song_id", "title"], List[str | None]]:
        """Select song from search results"""

        description_text = f"Search results. Keyword: {search_results['keyword']}."
        options_list = [
            f"{artist} - {title}"
            for artist, title in zip(search_results["artist"], search_results["title"])
        ]

        selected_idx_int = select_option(
            options=options_list, description=description_text
        )

        selected_title = search_results["title"][selected_idx_int]
        selected_id = search_results["song_id"][selected_idx_int]
        selected_artist = search_results["artist"][selected_idx_int]

        selected_result = {
            "title": selected_title,
            "song_id": selected_id,
            "artist": selected_artist,
        }

        return selected_result

    def __get_song_class(
        self,
        **kwargs,
    ) -> Song:
        """Create song class"""

        song_class = Song()
        song_class.title = kwargs["title"]
        song_class.song_id = kwargs["song_id"]
        song_class.artist = kwargs["artist"]

        return song_class

    def __get_song_scrap_lyrics(
        self,
        song_class: Song,
    ) -> Song:
        """Scrap lyrics"""

        song_url = f"https://www.melon.com/song/detail.htm?songId={song_class.song_id}"

        response = get(song_url, timeout=10, headers={"User-Agent": "XY"})
        html_parser = BeautifulSoup(response.text, "html.parser")
        lyrics = html_parser.find_all("div", class_="lyric")

        # Rectify lyrics
        remove_0 = '<div class="lyric" id="d_video_summary"><!-- height:auto; 로 변경시, 확장됨 -->'
        remove_1 = "</div>"
        remove_2 = "<br/>"

        lyrics = str(lyrics[0]).replace(remove_0, "")
        lyrics = lyrics.replace(remove_1, "")
        lyrics = lyrics.replace(remove_2, "\n")
        lyrics = str.strip(lyrics)

        song_class.lyrics_txt = lyrics

        return song_class

    def _get_song_lyrics(
        self,
        search_results: dict,
    ) -> Song:
        """Get song except lyrics dict"""

        selected_result = self.__select_song(search_results=search_results)
        song_class = self.__get_song_class(**selected_result)
        song_class = self.__get_song_scrap_lyrics(song_class=song_class)

        return song_class

    def get_song(self) -> Song:
        """Main function"""

        search_results = self._get_search()
        song_class = self._get_song_lyrics(search_results=search_results)

        return song_class


class SaveLyrics:
    """
    Save lyrics to txt file and json file.
    Also update the `song_class`.

    args:
        song_class: Song

    methods:
        save_lyrics: Save lyrics to txt and json
    """

    def __init__(
        self,
        song_class: Song,
    ) -> None:

        self.song_class: Song = song_class
        self.lyrics_txt: str = song_class.lyrics_txt

        self.filename: str = song_class.title
        self.filepath_txt: Path = Path(f"./data/lyrics/txt/{self.filename}.txt")
        self.filepath_json: Path = Path(f"./data/lyrics/json/{self.filename}.json")

        self.editor_options: List[str] = ["nano", "vim", "manual"]
        self.selected_editor_idx: int = -1

    def _save_as_txt(
        self,
    ) -> None:
        """
        Save lyrics as txt file.
        """

        filename = f"{self.filename}.txt"
        filepath = self.filepath_txt

        if filepath.exists():
            exists_options = ["Yes", "No"]

            exists_idx = select_option(
                options=exists_options,
                description=f"{filename} exists. Do you want to overwrite?",
            )

            if exists_options[exists_idx] == "Yes":
                filepath.unlink()
                with open(
                    file=filepath,
                    mode="w",
                    encoding="utf-8",
                ) as f:
                    f.write(self.lyrics_txt)
                    f.close()

            elif exists_options[exists_idx] == "No":
                print("Change discarded.")

        else:
            with open(
                file=filepath,
                mode="w",
                encoding="utf-8",
            ) as f:
                f.write(self.lyrics_txt)
                f.close()

    def __edit_txt_with_nano(
        self,
    ) -> None:
        """
        Edit existing txt file with nano editor.
        """

        subprocess.run(["nano", self.filepath_txt], check=True)

    def __edit_txt_with_vim(
        self,
    ) -> None:
        """
        Edit existing txt file with vim editor.
        """

        subprocess.run(["vim", self.filepath_txt], check=True)

    def __edit_txt_manually(
        self,
    ) -> None:
        """
        Edit txt file manually.
        """

        print(f"Go to {self.filepath_txt} and edit the txt file manually.")

        complete_flag = "".join(
            random.choices(string.ascii_letters + string.digits, k=5)
        )

        while input(f"Type {complete_flag} to finish editing: ") != complete_flag:
            continue

    def __edit_txt_select_editor(
        self,
    ) -> int:
        """
        Select editor for editing txt file.
        """

        editor_idx = select_option(
            options=self.editor_options,
            description="Select editor for editing txt file.",
        )

        return editor_idx

    def _edit_txt_terminal(
        self,
    ):
        """
        Edit txt file in terminal.
        """

        if self.selected_editor_idx == -1:
            editor_idx = self.__edit_txt_select_editor()
        else:
            editor_idx = self.selected_editor_idx

        if self.editor_options[editor_idx] == "nano":
            self.__edit_txt_with_nano()

        elif self.editor_options[editor_idx] == "vim":
            self.__edit_txt_with_vim()

        elif self.editor_options[editor_idx] == "manual":
            self.__edit_txt_manually()

        with open(file=self.filepath_txt, mode="r", encoding="utf-8") as f:
            self.song_class.lyrics_txt = f.read()
            f.close()

    def __is_idx(
        self,
        segment: str,
    ) -> bool:
        """Check if index letter exists in segment"""

        if len(segment) == 1:
            return True

        elif len(segment) == 2 and segment[1].isdigit():
            return True

        else:
            return False

    def _is_fit_style(
        self,
        txt_lyrics_path: str | Path,
    ) -> bool:
        """Check if txt lyrics is fit for json"""

        with open(file=txt_lyrics_path, mode="r", encoding="utf-8") as f:
            text_segments = f.read().split("\n")
            f.close()

        is_fit = True

        idx_exists = False
        for segment in text_segments:

            if len(segment) > 24:
                is_fit = False
                break

            if not idx_exists and self.__is_idx(segment=segment):
                idx_exists = True

        if not idx_exists:
            is_fit = False

        return is_fit

    def _separate_parts(
        self,
    ) -> None:
        """Separate lyrics to parts."""

        lyrics_txt: str = copy(self.song_class.lyrics_txt)
        lyrics_txt: str = lyrics_txt.strip()
        lyrics_txt_list: list[str] = lyrics_txt.split("\n")
        lyrics_dict: dict = {}

        for segment in lyrics_txt_list:
            current_segment: str = segment.strip()

            if self.__is_idx(segment=current_segment):
                part_idx = current_segment
                lyrics_dict[part_idx] = ""

            else:
                lyrics_dict[part_idx] += f"{current_segment}\n"

        self.song_class.lyrics_dict = lyrics_dict

    def _save_as_json(
        self,
    ) -> None:
        """Save lyrics as json file."""

        filepath = self.filepath_json

        if filepath.exists():
            filepath.unlink()

        with open(
            file=filepath,
            mode="w",
            encoding="utf-8",
        ) as f:
            json.dump(obj=self.song_class.lyrics_dict, fp=f, ensure_ascii=False)
            f.close()

    def save_lyrics(
        self,
    ) -> None:
        """Lyrics saving process."""

        self._save_as_txt()
        self._edit_txt_terminal()
        self._separate_parts()
        self._save_as_json()
