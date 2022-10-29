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
            return "未找到相关歌曲"
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
        if choice in range(1, 10):  # 最大支持九个选项
            choice = int(choice) - 1
            redis_cache = cls.rc.get('song_choices')
            json_cache = json.loads(
                redis_cache)  # json字符串解析为字典
            authentication = auth_id  # 发送者的id
            print(json_cache)
            if authentication == json_cache['auth']:  # 鉴权
                if choice <= len(json_cache['path']):
                    cls.rc.rpush('song_list', json_cache['path'][choice])
                    return '点歌成功，加入播放队列'
                else:  # 选择序号不能超过相关歌单列表长度
                    return '序号错误'
            else:
                return "你不是点歌的那位哦"
        else:
            return "点歌失败，请输入正确的选择序号（1~9）"
