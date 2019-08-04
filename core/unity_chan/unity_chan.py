import os
import cv2

from enum import Enum
import numpy as np
unity_chan_view_name = "UView"

class UnityChanState(Enum):
	Stand = 1,
	Damaged = 2,
	Run = 3,
	Jump = 4,

class UnityChanRenderer:
	def __init__(self):
		self.img_index = 0
		self.rendering_count = 0
		self.unity_chan_image = []
		self.code_location = os.path.dirname(os.path.abspath(__file__))
	
	def get_image_index(self):
		return self.rendering_count % len(self.unity_chan_image)

	def render(self, base_image, x, y, unity_chan_width, unity_chan_height):

		# print(f"rendering count : {self.rendering_count}")

		idx = self.get_image_index()

		base_height, base_width, base_depth = base_image.shape

		xx = x - int(unity_chan_width / 2)
		ww = unity_chan_width
		if xx < 0:
			ww = unity_chan_width + xx
			xx = 0
		if xx + unity_chan_width > base_width:
			xx -= xx + unity_chan_width - base_width

		yy = y - int(unity_chan_height / 2)
		hh = unity_chan_height
		if yy < 0:
			hh = unity_chan_height + yy
			yy = 0
		if yy + unity_chan_height > base_height:
			yy -= yy + unity_chan_height - base_height

		resized = cv2.resize(self.unity_chan_image[idx], (unity_chan_width, unity_chan_height))
		base_image[yy:yy+unity_chan_height, xx:xx+unity_chan_width] = resized

		self.rendering_count += 1

		# return base_image

class UnityChanRenderer_Stand(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.unity_chan_image = [
			cv2.imread(os.path.join(self.code_location, "image", "stand_1.png")),
			cv2.imread(os.path.join(self.code_location, "image", "stand_2.png")),
			cv2.imread(os.path.join(self.code_location, "image", "stand_3.png")),
		]
	def get_image_index(self):
		idx = 0
		if self.rendering_count % 10 == 0:
			idx = 2
		elif self.rendering_count % 2 == 0:
			idx = 1
		return idx

class UnityChanRenderer_Run(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.unity_chan_image = [
			cv2.imread(os.path.join(self.code_location, "image", "run_1.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_2.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_3.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_4.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_5.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_6.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_7.png")),
			cv2.imread(os.path.join(self.code_location, "image", "run_8.png")),
		]

class UnityChanRenderer_Jump(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.unity_chan_image = [
			cv2.imread(os.path.join(self.code_location, "image", "jump_1.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_2.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_3.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_4.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_5.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_6.png")),
			cv2.imread(os.path.join(self.code_location, "image", "jump_7.png")),
		]

class UnityChanView:
	def __init__(self):
		self.__unity_chan_state = UnityChanState.Run
		self.__renderer = {
			UnityChanState.Stand : UnityChanRenderer_Stand(),
			UnityChanState.Run : UnityChanRenderer_Run(),
			UnityChanState.Jump : UnityChanRenderer_Jump(),
		}

	def render(self, base_image, x, y, unity_chan_width, unity_chan_height):
		self.__renderer[self.__unity_chan_state].render(base_image, x, y, unity_chan_width, unity_chan_height)

	def stand(self): self.__unity_chan_state = UnityChanState.Stand
	def run(self):   self.__unity_chan_state = UnityChanState.Run
	def jump(self):  self.__unity_chan_state = UnityChanState.Jump

if __name__ == "__main__":

	view = UnityChanView()
	blank_image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)

	while True:
		view.render(blank_image, 100, 100, 80, 80)

		cv2.imshow("unity chan", blank_image)

		key = cv2.waitKey(150) & 0xFF
		if key == ord('q'):
			self.shown = False
			cv2.destroyAllWindows()
			print("exit")
		elif key == ord('a'):
			view.run()
		elif key == ord('s'):
			view.stand()
		elif key == ord(' '):
			view.jump()

