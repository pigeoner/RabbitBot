import re

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.event import Event
from nonebot.typing import Union
from nonebot_plugin_guild_patch import GuildMessageEvent  # DO NOT DELETE

from .obs_websocket import OBS_PLAY
from .search import Search
from .sql_redis import insert_redis


class zplay:
    def __init__(self, event, arg):
        self.arg = arg
        self.event = event
        self.tool = zplay_tool(self.event)
        self.redis = insert_redis()
        self.search = Search()
        self.uid = self.tool.user_id()
        self.obs = OBS_PLAY()

    async def song_select(self):
        result = self.search.walk_file(self.arg)
        print(result)
        if not result:
            return {"code": 400, "message": f"曲库中暂无{self.arg}"}
        else:
            if len(result) == 1:
                await self.redis.list_add(result[0], uid=str(self.uid))
                return {"code": 200, "message": f"已为您将{result[0]['song_name']}添加至播放列表"}
            else:
                song_name = [song_name['song_name'] for song_name in result]  # 将曲名list
                song_name = self.tool.insert_num(song_name)
                song_name = '\n'.join(song_name)
                seq_data = self.tool.seq_song(result)
                seq_data = self.tool.result_deal(result=seq_data, uid=str(self.uid))
                await self.redis.temp_result(seq_data)
                return {"code": 300, "message": song_name, "seq": seq_data}

    async def song_choose(self):
        int_key = self.tool.arg_int()[0]
        song_list = await self.redis.temp_get(self.uid)
        song_msg = song_list[int(int_key)] if int_key and int(int_key) <= len(song_list) else None
        if song_msg:
            await self.redis.list_add(song_msg, uid=str(self.uid))
            return {"code": 200, "message": f"已添加{song_msg}至播放列表"}
        else:
            return None


class zplay_tool:
    def __init__(self, event: Union[Event, GroupMessageEvent, GuildMessageEvent, PrivateMessageEvent]):
        self.event = event

    def arg_int(self):
        return re.search("\d+", str(self.message()))

    def info_group(self):
        return self.event.group_id

    def info_guild(self):
        return self.event.guild_id

    def info_channel(self):
        return self.event.channel_id

    def user_id(self) -> str:
        return str(self.event.user_id)

    def message(self):
        return self.event.message

    def reply_message(self):
        return self.event.reply.message

    def reply_sender(self):
        return self.event.reply.sender

    @staticmethod
    def insert_num(text) -> list:
        return [f"{i}.{song}" for i, song in enumerate(text, start=1)]

    @staticmethod
    def seq_song(text) -> dict:
        dict_type = {}
        for i, song in enumerate(text, start=1):
            dict_type[str(i)] = song
        return dict_type

    @staticmethod
    def result_deal(result: dict, uid: str):
        return {'uid': uid, 'data': result}
