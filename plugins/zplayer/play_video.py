import cv2
import subprocess
from plugins.config import _config

# 电梓播放器插件


class Video(object):
    def __init__(self, path):
        self.path = path

    def play(self):
        src = _config['test_src']
        rtmp = _config['video_play']['rtmp']
        cap = cv2.VideoCapture(src)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        sizeStr = str(size[0]) + 'x' + str(size[1])

        command = ['ffmpeg',
                   '-y', '-an',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', sizeStr,
                   '-r', '1',
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                   rtmp]

        pipe = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE
                                )

        while cap.isOpened():
            success, frame = cap.read()
            if success == False:
                print("Error")
                break
            img = cv2.resize(frame, size)
            pipe.stdin.write(img.tostring())
        cap.release()
        pipe.terminate()
        print('--------------结束了---------------')


class Movie_MP4(Video):
    type = 'MP4'
