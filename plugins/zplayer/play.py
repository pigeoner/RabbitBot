import cv2
import subprocess
import os
from random import choice
import time
from plugins.config import _config
import simpleobsws
import asyncio
from random import choice
import os
from time import sleep
import redis
from plugins.pool import get_redis_pool
import nest_asyncio
nest_asyncio.apply()

# 电梓播放器插件


class Video(object):
    redis_pool = get_redis_pool()
    rc = redis.Redis(connection_pool=redis_pool)
    # Create an IdentificationParameters object (optional for connecting)
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False)
    # Every possible argument has been passed, but none are required. See lib code for defaults.
    ws = simpleobsws.WebSocketClient(
        url=_config['obs_ws_url'], password=_config['obs_ws_password'], identification_parameters=parameters)

    @classmethod
    def ffmpeg_play(cls, filepath):
        rtmp = _config['video_play']['rtmp']
        cap = cv2.VideoCapture(filepath)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        sizeStr = str(size[0]) + 'x' + str(size[1])
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 帧数
        command = ['ffmpeg',
                   '-re',
                   '-i', filepath,
                   '-vcodec', 'copy',
                   '-acodec', 'aac',
                   '-pix_fmt', 'bgr24',
                   '-s', sizeStr,
                   '-r', str(fps),  # 好像是帧率
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   rtmp]

        pipe = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE,
                                stderr=subprocess.STDOUT, encoding='utf8', text=True)

        # while cap.isOpened():
        #     # for i in range(frame_count):
        #     success, frame = cap.read()
        #     if not success:
        #         print("Error")
        #         break
        #     img = cv2.resize(frame, size)
        #     pipe.stdout.write(img.tobytes())
        # cap.release()
        # pipe.terminate()
        # print('--------------结束了---------------')

        pipe.wait()
        if pipe.poll() == 0:
            print("success:", filepath)
        else:
            print("error:", filepath)

        time.sleep(3)

    @classmethod
    def get_random_song(cls):
        video_lst = []
        for root, dirs, files in os.walk(_config['video_path']):
            # root 表示当前正在访问的文件夹路径
            # dirs 表示该文件夹下的子目录名list
            # files 表示该文件夹下的文件list
            for file in files:
                if file.rsplit('.')[-1] == 'mp4':
                    video_lst.append(os.path.join(root, file))
        song_to_play = choice(video_lst)
        return song_to_play

    @classmethod
    def get_song_to_play(cls):
        song_list_len = cls.rc.llen('song_list')  # 已点歌曲列表长度
        if song_list_len > 0:
            song_to_play = cls.rc.lpop('song_list')
        else:
            song_to_play = cls.get_random_song()
        return song_to_play

    @classmethod
    async def obs_play(cls):
        async def make_request():
            await cls.ws.connect()  # Make the connection to obs-websocket
            # Wait for the identification handshake to complete
            await cls.ws.wait_until_identified()
            try:
                while True:
                    is_end = cls.rc.get('azusa_player_end')
                    is_end = int(is_end) if is_end else None
                    if not is_end:
                        print('接收到频道终止消息，结束播放')
                        break
                    song_to_play = cls.get_song_to_play()
                    request = simpleobsws.Request('SetInputSettings', {
                        'inputName': '电梓播放器',
                        'inputSettings': {
                            'local_file': song_to_play
                        }
                    })
                    ret = await cls.ws.call(request)  # Perform the request
                    if ret.ok():  # Check if the request succeeded
                        req = simpleobsws.Request('GetMediaInputStatus', {
                            'inputName': '电梓播放器'})
                        filename = os.path.basename(song_to_play)
                        print('准备播放视频：{}...'.format(filename))
                        end_info = '播放视频：{} 结束'.format(filename)
                        while True:
                            is_end = cls.rc.get('azusa_player_end')
                            is_end = int(is_end) if is_end else None
                            if not is_end:
                                break
                            sleep(1)
                            res = await cls.ws.call(req)
                            try:
                                if not res or not res.ok() or res.responseData['mediaState'] in [
                                        'OBS_MEDIA_STATE_ENDED',
                                        'OBS_MEDIA_STATE_STOPPED',
                                        'OBS_MEDIA_STATE_ERROR']:
                                    break
                            except Exception:
                                end_info = '播放视频：{} 异常，终止播放'.format(filename)
                                break
                        print(end_info)
                    else:
                        print('请求修改媒体源文件失败，结束播放')
                        break
            except KeyboardInterrupt:
                print('接收到键盘终止命令，电梓播放器结束')
            finally:
                await cls.ws.disconnect()  # Disconnect from the websocket server cleanly
        loop = asyncio.get_event_loop()
        loop.run_until_complete(make_request())

    @classmethod
    def end_play(self):
        self.rc.set('azusa_player_end', 0)


class Movie_MP4(Video):
    type = 'MP4'


if __name__ == '__main__':
    Movie_MP4.obs_play()
