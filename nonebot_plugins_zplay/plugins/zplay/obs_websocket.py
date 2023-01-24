import obsws_python as obs
from .search import Search
from .sql_redis import insert_redis
from nonebot import require
from ...config_zplay import obs_config


class OBS_PLAY:
    def __init__(self):
        self.obs_ws = obs.ReqClient(host=obs_config['obs_ws']['host'], port=obs_config['obs_ws']['port'])
        self.media = obs_config['media']
        self.scheduler = require('nonebot_plugin_apscheduler').scheduler
        self.scheduler.scheduled_job('interval', seconds=3, args='')
        self.search = Search()
        self.redis = insert_redis()

    @staticmethod
    async def data_media(song_path):
        return {'local_file': song_path}

    async def obs_change(self, song_path):
        self.obs_ws.set_input_settings(self.media, await self.data_media(song_path), True)

    async def random_select(self):
        random_song = self.search.random_song()
        await self.redis.play_now(random_song['song_name'])
        return random_song['song_path']
