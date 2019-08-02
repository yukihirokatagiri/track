import cv2

import sys
sys.path.insert(0, "core")
import config

class ImageStream:
	def __init__(self):
		self.source = None
		self.capture = None

	def open(self):
		self.capture = cv2.VideoCapture(self.source)

	def close(self):
		self.capture.release()

	def isOpened(self):
		return self.capture.isOpened()

	def read(self):
		return self.capture.read()

class Camera(ImageStream):
	def __init__(self):
		self.source = config.CAMERA_ID

class FileStream(ImageStream):
	def __init__(self):
		self.source = config.INPUT_FILE
