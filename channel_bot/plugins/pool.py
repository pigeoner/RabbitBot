import aiomysql
from .config import _config
import redis


async def get_pool():
    pool = await aiomysql.create_pool(host=_config['mysql']['host'], user=_config['mysql']['user'],
                                      password=_config['mysql']['password'], db=_config['mysql']['db'], charset='utf8', autocommit=True)
    return pool


def get_redis_pool():
    redis_pool = redis.ConnectionPool(
        host=_config['redis']['host'], port=_config['redis']['port'], db=_config['redis']['db'], password=_config['redis']['password'], decode_responses=True)
    return redis_pool
