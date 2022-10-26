from logger import logger
from .play import Movie_MP4
from .search import Search
import json
from plugins.config import _config
import redis
from plugins.pool import get_redis_pool


class Song:
    redis_pool = get_redis_pool()
    rc = redis.Redis(connection_pool=redis_pool)

    @classmethod
    def select_song(cls, song_title, auth_id):
        logger.info(song_title)
        srch = Search()
        song_path_lst, song_name_lst = srch.walk_file(
            _config['video_path'], song_title)  # 找歌
        if len(song_path_lst) == 1:
            cls.rc.rpush('song_list', song_path_lst[0])
            logger.info(song_path_lst[0])
            return "点歌成功，加入播放队列"
        elif len(song_path_lst) == 0:
            return "taxi了，找不到捏"
        elif len(song_path_lst) > 1:
            song_name_lst = [f"{i+1}.{song.rsplit('.', 1)[0]}"
                             for i, song in enumerate(song_name_lst)]
            json_content = {
                'auth': auth_id,  # 用于鉴权
                'path': song_path_lst
            }
            song_choices = json.dumps(json_content, ensure_ascii=False)
            cls.rc.set('song_choices', song_choices)
            result = '\n'.join(song_name_lst[0:])
            return result

    @classmethod
    def choose_song(cls, choice, auth_id):
        if choice == '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9':  # 最大支持九个选项
            choice = int(choice) - 1
            redis_cache = cls.rc.get('song_choices')
            json_cache = json.loads(
                redis_cache)  # json字符串解析为字典
            authentication = auth_id  # 发送者的id
            print(json_cache)
            if authentication == json_cache['auth']:  # 鉴权
                cls.rc.rpush('song_list', json_cache['path'][choice])
                return '点歌成功，加入播放队列'
            else:
                return "你不是点歌的那位哦"
        else:
            return "哥们再输一遍，听不懂"
