import requests  # pip下载的py库文件
import json  # py内置
import os
from plugins.config import _config


class UpdateBili:
    def __init__(self):
        self.video_path = _config['video_path']
        self.cookie = _config['cookie']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Cookie': self.cookie
        }
        self.video_url = 'https://api.bilibili.com/x/web-interface/view?bvid='
        self.download_url = 'https://api.bilibili.com/x/player/playurl?cid={}&avid={}&qn={}'

    def get_video_info(self, bv):
        r = requests.get(url=self.video_url+bv, headers=self.headers)
        if (not r) or r.json()['code']:
            raise Exception('获取视频信息失败')
        video_info = r.json()
        return video_info

    def get_download_info(self, cid, avid, qn):
        r = requests.get(url=self.download_url.format(
            cid, avid, qn), headers=self.headers)
        if (not r) or r.json()['code']:
            raise Exception('获取视频下载信息失败')
        download_info = r.json()
        return download_info

    def get_cid_list(self, bv):  # 获取视频的p数
        video_info = self.get_video_info(bv)
        list_num = len(video_info['data']["pages"])
        return list_num

    def get_cid_one(self, bv):  # 获取单p视频的cid
        video_info = self.get_video_info(bv)
        return video_info['data']["cid"]

    def get_cid_more(self, bv):  # 获取多p视频的cid
        video_info = self.get_video_info(bv)
        cid_list = [page['cid'] for page in video_info['data']['pages']]
        return cid_list

    def get_cid_more_one(self, bv, p):  # 获取多p指定视频的cid
        video_info = self.get_video_info(bv)
        cid = video_info['data']["pages"][p - 1]['cid']
        return cid

    def get_aid(self, bv):  # 获取aid
        video_info = self.get_video_info(bv)
        return video_info["data"]["aid"]

    def get_title(self, bv):  # 获取视频标题
        video_info = self.get_video_info(bv)
        return video_info['data']["title"]

    def get_part(self, bv, p):  # ?
        video_info = self.get_video_info(bv)
        return video_info['data']["pages"][p - 1]['part']

    def get_download_url_one(self, bv):  # 获取下载链接
        download_info = self.get_download_info(
            self.get_cid_one(bv), self.get_aid(bv), 116)
        return download_info['data']['durl'][0]['url']

    def get_download_url_more(self, bv, p):  # 获取多p下载链接
        download_info = self.get_download_info(p, self.get_aid(bv), 116)
        return download_info['data']['durl'][0]['url']

    def get_url_only(self, bv, p):  # 获取多p中指定下载链接
        download_info = self.get_download_info(
            self.get_cid_more_one(bv, p), self.get_aid(bv), 116)
        return download_info['data']['durl'][p - 1]['url']

    # 主体部分

    def download_video(self, url, bv, filename):
        _headers = self.headers.copy()
        _headers['referer'] = 'https://www.bilibili.com/video/' + bv
        try:
            with requests.get(url=url, headers=_headers, stream=True) as r:
                content_length = r.headers['content-length']
                with open(filename, mode='wb') as f:  # 下载视频到D盘，并以标题命名，文件格式为MP4
                    rate = 1
                    for i in r.iter_content(chunk_size=4096):
                        loaded = int(
                            100*(rate * 4096.0 / int(content_length)))  # 进度
                        f.write(i)
                        print(f'\r已下载 {loaded}%', end='', flush=True)
                        rate += 1
                    print()
        except Exception as e:
            print(e)
            raise Exception('获取视频下载内容时出错\n', e)

    def download_video_bili(self, bv):
        cid_list_len = self.get_cid_list(bv)
        if cid_list_len == 0:
            return '戳啦戳啦'
        elif cid_list_len == 1:
            url = self.get_download_url_one(bv)
            filename = self.video_path + self.get_title(bv) + '.mp4'
            self.download_video(url, bv, filename)
        elif cid_list_len > 1:
            for p in self.get_cid_more(bv):
                url = self.get_download_url_more(bv, p)
                filename = self.video_path + \
                    self.get_title(bv) + self.get_part(bv, p) + '.mp4'
                self.download_video(url, bv, filename)
        return '已为您下载完毕'

    def download_video_bili_more_one(self, bv, p):
        url = self.get_download_url_more(bv, p)
        cid_list_len = self.get_cid_list(bv)
        filename = self.video_path + \
            self.get_title(bv) + self.get_part(bv, p) + '.mp4'
        if cid_list_len > 0:
            self.download_video(url, bv, filename)
            return '已为您下载完毕'
        if cid_list_len == 0:
            return '戳啦戳啦'
