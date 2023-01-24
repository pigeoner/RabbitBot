from random import choice
import os


async def get_dz():
    dz_folder = './assets/dingzhen'
    dz = choice(os.listdir(dz_folder))
    with open(os.path.join(dz_folder, dz), 'rb') as f:
        return f.read()
