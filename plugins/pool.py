import aiomysql
from .config import _config


async def get_pool():
    pool = await aiomysql.create_pool(host=_config['mysql']['host'], user=_config['mysql']['user'],
                                      password=_config['mysql']['password'], db=_config['mysql']['db'], charset='utf8', autocommit=True)
    return pool
