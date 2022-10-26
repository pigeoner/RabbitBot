import cv2
import subprocess
import os
from random import choice
import time
from plugins.config import _config

# 电梓播放器插件


class Video(object):
    @classmethod
    def play(cls, filepath):
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
    def random_play(cls):
        video_lst = []
        for root, dirs, files in os.walk(_config['video_path']):
            # root 表示当前正在访问的文件夹路径
            # dirs 表示该文件夹下的子目录名list
            # files 表示该文件夹下的文件list
            for file in files:
                if file.rsplit('.')[-1] == 'mp4':
                    video_lst.append(os.path.join(root, file))
        video_file = choice(video_lst)
        cls.play(video_file)


class Movie_MP4(Video):
    type = 'MP4'


if __name__ == '__main__':
    Movie_MP4.random_play()
