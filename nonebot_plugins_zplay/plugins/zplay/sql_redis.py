import redis
import json
import asyncio
import sys
sys.path.append('..')

from config_zplay import obs_config

set_expired_time = obs_config['set_expired_time']
redis_pool = redis.ConnectionPool(host=obs_config['redis']['host'],
                                  password=obs_config['redis']['password'],
                                  port=obs_config['redis']['port'],
                                  decode_responses=True)


class insert_redis:
    def __init__(self):
        self.redis_conn = redis.Redis(connection_pool=redis_pool)

    async def temp_result(self, result: dict):
        """
        缓存点歌数据
        :param result: dict
        - uid: str 用户uid
        - data: dict 点歌数据
        :return: None
        """
        uid = result['uid']
        data = result['data']
        self.redis_conn.hset(name="temp_" + uid, key=uid, value=json.dumps(data))
        self.redis_conn.expire("temp_" + uid, set_expired_time)
        self.redis_conn.close()

    async def temp_get(self, uid: str):
        result = self.redis_conn.hget(name="temp_" + uid, key=uid)
        self.redis_conn.close()
        return json.loads(result) if result else None

    async def list_add(self, search_result, uid):
        self.redis_conn.lpush('song_list_name', search_result['song_name'])
        self.redis_conn.lpush('song_list_path', search_result['song_path'])
        self.redis_conn.lpush('song_list_uid', uid)
        self.redis_conn.close()

    async def list_to_play(self):
        name = self.redis_conn.brpop('song_list_name', timeout=1)
        path = self.redis_conn.brpop('song_list_path', timeout=1)
        uid = self.redis_conn.brpop('song_list_uid', timeout=1)
        if name:
            await self.play_now(song_name=name[1])
            return [path[1], uid[1], name[1]]
        else:
            self.redis_conn.close()
            return None

    async def list_all(self):
        name = self.redis_conn.lrange('song_list_name', 0, -1)
        self.redis_conn.close()
        return name[::-1]

    async def play_now(self, song_name=None, is_del=False):
        """
        获取正在播放的曲目
        当song_name_有值时，更改当前值
        当is_del为T时， 删除当前值
        """
        self.redis_conn.delete('play_now') if is_del else None
        self.redis_conn.set('play_now', value=song_name) if song_name else None
        self.redis_conn.close()
        return self.redis_conn.get('play_now') if not song_name and not is_del else None


if __name__ == '__main__':
    insert = insert_redis()
    asyncio.run(insert.list_all())
