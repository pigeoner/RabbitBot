import requests
import json
import time
import asyncio
import nest_asyncio

nest_asyncio.apply()
from ...config_zplay import obs_config

My_path = obs_config['fold_path']


class download_bili:
    def __init__(self, bv, roster: list = None):
        """
        调用一个BV对象
        :param bv: 视频bv
        :param roster: 多p视频中需要下载的视频p号 若无指定，则全部下载
        """
        self.bv = bv
        self.roster = roster
        self.url_bvid = 'https://api.bilibili.com/x/web-interface/view?bvid='
        self.url_cid = 'https://api.bilibili.com/x/player/playurl?'
        self.url_dl = 'https://api.bilibili.com/x/player/playurl?cid={}&avid={}&qn={}'
        self.user_agent = obs_config['User-Agent']
        self.cookie = obs_config['Cookie']
        self.referer = obs_config['referer']
        self.headers_u = {
            'User-Agent': self.user_agent
        }
        self.headers_c = {
            'user-agent': self.user_agent,
            'Cookie': self.cookie,
        }
        loop = asyncio.get_event_loop()
        self.info = loop.run_until_complete((self.get_video_info(self.bv)))
        self.tool = download_tool(self.info)

    async def get_video_info(self, bv):  # 获取视频的信息
        url = self.url_bvid + bv
        return json.loads(requests.get(url=url, headers=self.headers_u).text)

    async def url_main(self):  # 获取单p视频下载链接
        url = self.url_dl.format(self.tool.data_cid(), self.tool.data_aid(), 116)
        return json.loads(requests.get(url=url, headers=self.headers_c).text)['data']['durl'][0]['url']

    async def url_batch(self):  # 获取多p视频下载链接
        cid_list = await self.tool.tool_cid(num=self.roster)
        url_list = [self.url_dl.format(cid, self.tool.data_aid(), 116) for cid in cid_list]
        return [json.loads(requests.get(url=url, headers=self.headers_c).text)['data']['durl'][0]['url']
                for url in url_list]

    async def download_video_bili(self, url, part: bool = False, num: int = None):
        """
        下载视频，单独调用本函数时url参数填url_main()
        :param url: 下载url
        :param part: 是否为多part视频
        :param num: part num
        :return:
        """
        headers = {
            'user-agent': self.user_agent,
            'Cookie': self.cookie,
            'referer': self.referer + self.bv
        }
        name = My_path + self.tool.data_title() + '.mp4' if not part \
            else My_path + self.tool.data_title() + await self.tool.page_part(num) + '.mp4'
        with open(name, mode='wb') as f:
            f.write(requests.get(url=url, headers=headers).content)
        return True

    async def download_batch(self):  # 批量下载
        for url, num in zip(await self.url_batch(), self.roster):
            print(url)
            await self.download_video_bili(url=url, part=True, num=num)

    async def deal_info(self, event_id, uid):
        if self.info["code"] == -400:
            return {"code": 400, "message": "找不到该视频"}
        elif self.tool.bool_is_p:
            return {"code": 400, "message": "暂不支持多part视频下载"}
        message = f'视频bv: {self.bv}\n' \
                  f'标题：{self.tool.data_title()}\n' \
                  f'发布日期：{await self.tool.get_time(self.tool.data_pubdate())}\n' \
                  f'类别：{self.tool.data_tname()}\n' \
                  f'up主：{self.tool.owner_name()}\n' \
                  f'观看量：{self.tool.stat_view()}\n' \
                  f'event_id({event_id})\n' \
                  f'user_id({uid})\n' \
                  f'bv({self.bv})\n' \
                  f'如果你认为该视频可以通过审核，请回复该条消息并输入‘审核t’，反之为‘审核f’\n' \
                  f'https://www.bilibili.com/video/{self.bv}'
        return {"code": 200, "message": message, "pic": self.tool.data_pic(), "id": event_id,
                "data": {"bv": self.bv, "uid": uid}}


class download_tool:
    """
    视频信息提取工具函数
    """

    def __init__(self, info):
        self.info = info
        if self.info["code"] == 0:
            self.data = self.info['data']
            self.owner = self.data['owner']
            self.stat = self.data['stat']
            self.pages = self.data['pages']
            self.bool_is_p = False if len(self.pages) == 1 else True
        else:
            self.data = None
            self.owner = None
            self.stat = None
            self.pages = None
            self.bool_is_p = False

    def data_title(self):  # 标题
        return self.data['title']

    def data_pic(self):  # 封面
        return self.data['pic']

    def data_ctime(self):  # 创建时间
        return self.data["ctime"]

    def data_desc(self):  # 简介
        return self.data["desc"]

    def data_tname(self):  # 类别
        return self.data["tname"]

    def data_pubdate(self):  # 发布日期
        return self.data["pubdate"]

    def data_cid(self):  # cid
        return self.data['cid']

    def data_aid(self):
        return self.data['aid']

    def owner_mid(self):
        return self.owner['mid']

    def owner_name(self):  # up
        return self.owner['name']

    def stat_view(self):  # 浏览量
        return self.stat['view']

    def stat_danmu(self):  # 弹幕数
        return self.stat["danmaku"]

    def stat_reply(self):  # 评论数
        return self.stat['reply']

    def stat_like(self):  # 点赞数
        return self.stat['like']

    def stat_favorite(self):  # 收藏数
        return self.stat["favorite"]

    def stat_coin(self):  # 投币数
        return self.stat["coin"]

    def stat_share(self):  # 分享数
        return self.stat['share']

    def stat_now_rank(self):  # 目前排名
        return self.stat["now_rank"]

    def stat_his_rank(self):  # 历史排名
        return self.stat["his_rank"]

    def bool_p(self):  # 是否多part
        return True if len(self.pages) > 1 else False

    async def page_cid(self, num):  # 提取part cid
        return self.pages[num - 1]['cid'] if len(self.pages) >= num - 1 else False

    async def page_part(self, num):  # 提取part 名称
        return self.pages[num - 1]['part'] if len(self.pages) >= num - 1 else False

    async def tool_cid(self, num: list):  # 批量提取cid
        return [self.page_cid(num) for num in num if self.page_cid(num)]

    @staticmethod
    async def get_time(the_time):  # 获取发送时间
        the_time = time.localtime(int(the_time))
        the_time = time.strftime("%m-%d %H:%M:%S", the_time)
        return the_time


if __name__ == '__main__':
    dl = download_bili('BV14g411k7Zc', [1, 2, 5])
    print(dl.info)
    # dl.get_url()
