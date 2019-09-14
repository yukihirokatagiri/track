import cv2
import config


class ImageStream:
    def __init__(self):
        self.source = None
        self.capture = None
        self.last_frame = None

    def open(self):
        self.capture = cv2.VideoCapture(self.source)

    def close(self):
        self.capture.release()

    def isOpened(self):
        return self.capture.isOpened()

    def read(self):
        success, self.last_frame = self.capture.read()
        if not success:
            self.last_frame = None
        return self.last_frame

    def get_size(self):
        if self.last_frame is None:
            return None
        else:
            height, width, depth = self.last_frame.shape
            return height, width


class Camera(ImageStream):
    def __init__(self):
        self.source = config.CAMERA_ID


class FileStream(ImageStream):
    def __init__(self):
        self.source = config.INPUT_FILE
