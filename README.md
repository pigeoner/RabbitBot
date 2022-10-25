# RabbitBot

一个没什么用的 QQ 频道机器人

## 使用

### 1.申请 bot

官网：https://q.qq.com/#/app/bot

### 2.安装依赖（已包含 qqbot python SDK）

```bash
pip install -r requirements.txt
```

### 3.配置

将 `config.bak.yaml` 重命名为 `config.yaml`，然后在 `config.yaml` 中配置你的 bot

## 注意

- `danmaku` 无法通过 pip 直接安装，需要自行下载安装，参考[THMonster/danmaku](https://github.com/THMonster/danmaku),将仓库下载到第三方库对应的目录下执行 `python setup.py install` 即可
