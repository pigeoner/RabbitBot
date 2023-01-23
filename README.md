# RabbitBot

一个超只因有用的 QQ 频道机器人

## QQ频道官方bot
## 使用

### 1.申请 bot

官网：https://q.qq.com/#/app/bot

### 2.安装依赖（已包含 qqbot python SDK）

```bash
pip install -r requirements.txt
```

### 3.配置

- 将 `config.bak.yaml` 重命名为 `config.yaml`，然后在 `config.yaml` 中配置你的 bot
- **电梓播放器相关配置**
  - 下载 [OBS Studio](https://obsproject.com/)
    和 [obs-websocket](https://github.com/obsproject/obs-websocket/releases/tag/5.0.1)
  - 在 `来源` 列表左下角选择 `添加` -> `媒体源`，命名为 `电子播放器`，或者自定义名称，并在 `config.yaml`
    文件里将 `input_name` 一项修改为自定义的名称
  - 在 OBS 的 `设置` 中填入个人 QQ 频道直播的推流地址和推流码
  - 开始推流

## 注意

- `danmaku` 无法通过 pip 直接安装，需要自行下载安装，参考[THMonster/danmaku](https://github.com/THMonster/danmaku)
  ,将仓库下载到第三方库对应的目录下执行 `python setup.py install` 即可

## NoneBot2

如果你习惯于使用NoneBot，则可以使用nonebot_plugins_zplay

## 使用

### 1.添加插件

将 `nonebot_plugins_zplay` 复制到 NoneBot文件夹中的 `plugins`
中，参考[Nonebot2/插件入门](https://nb2.baka.icu/docs/tutorial/plugin/introduction)

### 2.安装依赖（包含nb-cli）

在插件目录中

```bash
pip install -r requirements.txt
```

### 3.配置

配置如上

## 注意

本人测试环境为Python 3.9 及 3.10，建议使用者的使用环境不低于 3.9

该插件目前仅适配电梓播放器

### TODO

新增更新模块
