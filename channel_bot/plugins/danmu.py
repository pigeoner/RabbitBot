import asyncio
import danmaku


async def printer(q, channel_id, message_id, post_msg, get_danmu=False):
    while True:
        msg = await q.get()
        if msg['msg_type'] == 'other' and type(msg) == dict:
            if type(msg['content']) == dict and msg['content']['cmd'] == 'SUPER_CHAT_MESSAGE':
                try:
                    msg_ = msg['content']['data']
                    msg_ = f"【{msg_['medal_info']['medal_name']}|{msg_['medal_info']['medal_level']}】{msg_['user_info']['uname']}[￥{msg_['price']}]：{msg_['message']}"
                    await post_msg(channel_id=channel_id, msg_id=message_id, content=msg_)
                except Exception as e:
                    pass
        elif msg['msg_type'] == 'danmaku' and type(msg) == dict:
            try:
                msg_ = f"【{msg['name']}】：{msg['content']}"
                await post_msg(channel_id=channel_id, msg_id=message_id, content=msg_)
            except Exception as e:
                pass


async def danmu_recorder(channel_id, message_id, post_msg, room_id, get_danmu=False):
    global loop
    global dmc
    q = asyncio.Queue()
    if not room_id:
        room_id = '605'
    dmc = danmaku.DanmakuClient(
        f'https://live.bilibili.com/{room_id}', q)
    loop = asyncio.create_task(printer(q, channel_id, message_id, post_msg))
    await dmc.start()

# asyncio.run(main())
