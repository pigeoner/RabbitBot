import os
import random
from typing import TypedDict
import sys
sys.path.append('..')

from config_zplay import obs_config


class search_result(TypedDict):
    song_path: str
    song_name: str


class Search:
    def __init__(self):
        self.fold_path = obs_config['fold_path']

    def walk_file(self, filename: str = 'mp4'):
        """
        :param filename: 待查找的文件名称
        :returns:
            - List:
                - song_path: 曲目路径
                - song_name: 曲目名称
        """
        back = None
        for root, dirs, files in os.walk(self.fold_path):
            back = [search_result(song_path=os.path.join(root, file), song_name=file.rstrip(".mp4"))
                    for file in files if filename in file]
        return back if any(back) else None

    def random_song(self):
        return random.choice(self.walk_file())


if __name__ == '__main__':
    se = Search()
    print(se.walk_file('爱情废柴'))
    print(se.random_song())
