import botpy
from botpy.types.message import Message
from botpy.ext.cog_yaml import read
from plugins import *
from plugins import _config
import re
import asyncio


class MyClient(botpy.Client):
    async def on_at_message_create(self, message: Message):
        await self.api.post_message(channel_id=message.channel_id, content="content")

    async def on_message_create(self, message: Message):
        msg = ''
        if message.content == 'ybb' and message.channel_id == _config['channel_id']['ybb']:
            msg = await get_ybb(message=message)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=msg)
        elif message.content == '竞速榜' and message.channel_id == _config['channel_id']['ybb']:
            msg = await get_ybb_lst(self.api.get_guild_member, message=message)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=msg)
        elif message.content == '反向竞速榜' and message.channel_id == _config['channel_id']['ybb']:
            msg = await get_ybb_lst(self.api.get_guild_member, message=message, order='asc')
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=msg)
        elif (mtc := re.match('^(查成分)\s+(\d+)$', message.content)) is not None:
            uid = mtc.group(2)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, image='http://bh.ayud.top/bili/usergp.php?uid='+uid)
        elif message.content == '一眼丁真':
            dz = await get_dz()
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, file_image=dz)
        elif (dm := re.match('^(弹幕启动)\s+(\d+)$', message.content)) is not None and message.channel_id == _config['channel_id']['danmu_test']:
            room_id = str(dm.group(2))
            asyncio.run(await danmu_recorder(message.channel_id, message.id, self.api.post_message, room_id, True))
        elif message.content == '弹幕启动':
            if message.channel_id == _config['channel_id']['danmu']['xiaoke']:
                room_id = '605'  # 小可
            elif message.channel_id == _config['channel_id']['danmu']['azi']:
                room_id = '510'  # 阿梓
            elif message.channel_id == _config['channel_id']['danmu']['qihai']:
                room_id = '21452505'  # 七海
            asyncio.run(await danmu_recorder(message.channel_id, message.id, self.api.post_message, room_id))
        elif (song_match := re.match('/点歌\s+(.*)', message.content)) is not None:
            song_title = song_match.group(1)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=select_song(song_title, message.author.id))
        elif (choice_match := re.match('/选择\s+(\d)', message.content)) is not None:
            choice = choice_match.group(1)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=choose_song(choice, message.author.id))
        elif (update_match := re.match('/更新\s+(.*)', message.content)) is not None:
            up_bili = UpdateBili()
            update_bv = update_match.group(1)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=up_bili.download_video_bili(bv=update_bv))
        elif (update_p_match := re.match('/指定更新\s+(.*)\s+(.*)', message.content)) is not None:
            up_bili_p = UpdateBili()
            update_bv = update_p_match.group(1)
            update_p = update_p_match.group(2)
            await self.api.post_message(channel_id=message.channel_id, msg_id=message.id, content=up_bili_p.download_video_bili_more_one(bv=update_bv, p=update_p))


intents = botpy.Intents(public_guild_messages=True, guild_messages=True)
client = MyClient(intents=intents)
client.run(appid=_config['appid'], token=_config['token'])
