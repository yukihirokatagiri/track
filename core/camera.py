import cv2
import numpy as np

import sys
sys.path.insert(0, "core")
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

class StaticImage():
	def __init__(self, image_path):
		self.source = None
		self.image_path = image_path
		self.img = None
		self.opened = False

	def open(self):
		self.opened = True

	def close(self):
		self.opened = False

	def isOpened(self):
		return self.opened

	def read(self):
		if self.image_path is None:
			return None
		else:
			self.img = cv2.imread(self.image_path)
		return self.img

	def get_size(self):
		if self.img is None:
			return None
		else:
			height, width, depth = self.img.shape
			return height, width
