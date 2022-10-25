from logger import logger
from .play_video import Movie_MP4
from .search_file import Search
import json
import codecs
import os
from plugins.config import _config


def select_song(song_title, auth_id):
    logger.info(song_title)
    srch = Search()
    song_path_lst, song_name_lst = srch.walk_file(
        _config['my_path'], song_title)  # 找歌
    if len(song_path_lst) == 1:
        movie = Movie_MP4(song_path_lst[0])
        movie.play()
        logger.info(song_path_lst[0])
        return "来咯来咯"
    elif len(song_path_lst) == 0:
        return "taxi了，找不到捏"
    elif len(song_path_lst) > 1:
        song_name_lst = [f"{i}.{song.rsplit('.', 1)[0]}"
                         for i, song in enumerate(song_name_lst)]
        json_content = {
            'auth': auth_id,  # 用于鉴权
            'path': song_path_lst
        }
        json_str = json.dumps(json_content)
        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        filename = codecs.open("./cache/result_temp.json", 'w+', 'utf-8')
        filename.write(json_str)  # 在缓存中写入
        result = '\n'.join(song_name_lst[0:])
        return result


def choose_song(choice, auth_id):
    if choice == '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9':  # 最大支持九个选项
        choice = int(choice) - 1
        filename = codecs.open(
            "./cache/result_temp.json", 'r', 'utf-8')  # 打开缓存的json文件
        json_cache = json.load(filename)  # json字符串解析为字典
        authentication = auth_id  # 发送者的id
        if authentication == json_cache['auth']:  # 鉴权
            movie = Movie_MP4(json_cache['path'][choice])  # 播放
            movie.play()
            return '正在为你播放'
        else:
            return "你不是点歌的那位哦"
    else:
        return "哥们再输一遍，听不懂"
