import yaml
import os

rootpath = os.path.dirname(os.path.dirname(__file__))


def get_config():
    with open(os.path.join(rootpath, 'config.yaml'), 'r', encoding='utf8') as f:
        config = yaml.safe_load(f)
    return config


_config = get_config()

if __name__ == '__main__':
    print(type(get_config()))
