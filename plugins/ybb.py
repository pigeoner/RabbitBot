from botpy.types.message import Message
from datetime import date
from random import random
from aiomysql import DictCursor
from .pool import get_pool


async def get_ybb(message: Message):
    guild_id = message.guild_id
    pool = await get_pool()
    conn = await pool.acquire()
    cursor = await conn.cursor(DictCursor)
    await cursor.execute('select uid from ybb where guild_id=%s', guild_id)
    ids = await cursor.fetchall()
    id_lst = [e['uid'] for e in ids]
    ybbdate = date.today().strftime('%Y-%m-%d')
    speed = int(random()*1e3)
    msg = ''
    username = message.author.username
    uid = message.author.id
    if uid not in id_lst:
        await cursor.execute("insert into ybb(uid,speed,date,guild_id) values(%s,%s,%s,%s)",
                             [uid, speed, ybbdate, guild_id])
        id_lst.append(uid)
        msg = f"{username}，你今天的小火车速度为{speed}km/h，看我把你绑在铁轨上"
    else:
        await cursor.execute('select * from ybb where uid=%s and guild_id=%s', [uid, guild_id])
        user = await cursor.fetchone()
        if date.today() > user['date']:
            await cursor.execute(
                'update ybb set speed = %s,date=%s where uid = %s and guild_id=%s', [speed, ybbdate, uid, guild_id])
            msg = f"{username}，你今天的小火车速度为{speed}km/h，看我把你绑在铁轨上"
        elif date.today() == user['date']:
            msg = f"{username}，你今天已经被创过了，明天再来吧"
    conn.close()
    return msg


async def get_ybb_lst(get_userinfo, message: Message, order: str = 'desc'):
    guild_id = message.guild_id
    pool = await get_pool()
    conn = await pool.acquire()
    cursor = await conn.cursor(DictCursor)
    ybbdate = date.today().strftime('%Y-%m-%d')
    exec_sql = 'select * from ybb where guild_id=%s and date >= %s order by speed ' + order
    await cursor.execute(exec_sql, [guild_id, ybbdate])
    rac_lst = await cursor.fetchall()
    rac_lst = rac_lst[:10]
    msg = f"本频道{'前' if order=='desc' else '后'}十位：\n"
    for i, r in enumerate(rac_lst):
        userinfo = await get_userinfo(guild_id=guild_id, user_id=r['uid'])
        username = userinfo['nick']
        msg += f"{username} {r['speed']}km/h\n" if i < len(
            rac_lst) - 1 else f"{username} {r['speed']}km/h"
    return msg
