import cv2
import pafy

class VideoStream:
    """
    VideoStream is a wrapper around cv2.VideoCapture.
    """

    def __init__(self, path):
        if path.startswith('https://'):
            video = pafy.new(path)
            streams = video.streams
            for stream in streams:
                print(stream)
            best = video.getbest(preftype='mp4')
            self.stream = cv2.VideoCapture(best.url)
        else:
            self.stream = cv2.VideoCapture(path)

    def read(self):
        """
        Return the next frame in the stream.
        """
        return self.stream.read()[1]

    def __del__(self):
        self.stream.release()