import cv2
import subprocess
from plugins.config import _config

# 电梓播放器插件


class Video(object):
    def __init__(self, filepath):
        self.src = filepath

    def play(self):
        rtmp = _config['video_play']['rtmp']
        cap = cv2.VideoCapture(self.src)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        sizeStr = str(size[0]) + 'x' + str(size[1])
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 帧数
        command = ['ffmpeg',
                   '-re',
                   '-i', self.src,
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

        # # while cap.isOpened():
        # for i in range(frame_count):
        #     success, frame = cap.read()
        #     if not success:
        #         print("Error")
        #         break
        #     img = cv2.resize(frame, size)
        #     pipe.stdout.buffer.write(img.tobytes())
        # cap.release()
        # pipe.terminate()
        # print('--------------结束了---------------')

        pipe.wait()
        if pipe.poll() == 0:
            print("success:", self.src)
        else:
            print("error:", self.src)


class Movie_MP4(Video):
    type = 'MP4'
