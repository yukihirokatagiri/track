import cv2
from enum import Enum

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
		self.img = []

	def render(self):
		print(f"rendering count : {self.rendering_count}")
		idx = self.rendering_count % len(self.img)
		cv2.imshow(unity_chan_view_name, self.img[idx])
		self.rendering_count += 1

class UnityChanRenderer_Stand(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.img = [
			cv2.imread("stand_1.png"),
			cv2.imread("stand_2.png"),
			cv2.imread("stand_3.png"),
		]

	def render(self):
		idx = 0
		if self.rendering_count % 10 == 0:
			idx = 2
		elif self.rendering_count % 2 == 0:
			idx = 1

		cv2.imshow(unity_chan_view_name, self.img[idx])

		self.rendering_count += 1

class UnityChanRenderer_Run(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.img = [
			cv2.imread("run_1.png"),
			cv2.imread("run_2.png"),
			cv2.imread("run_3.png"),
			cv2.imread("run_4.png"),
			cv2.imread("run_5.png"),
			cv2.imread("run_6.png"),
			cv2.imread("run_7.png"),
			cv2.imread("run_8.png"),
		]


class UnityChanRenderer_Jump(UnityChanRenderer):
	def __init__(self):
		super().__init__()

		# todo : read image only once and split the image. We only need to load file only once.
		self.img = [
			cv2.imread("jump_1.png"),
			cv2.imread("jump_2.png"),
			cv2.imread("jump_3.png"),
			cv2.imread("jump_4.png"),
			cv2.imread("jump_5.png"),
			cv2.imread("jump_6.png"),
			cv2.imread("jump_7.png"),
		]

class UnityChanView:
	def __init__(self):
		self.__unity_chan_state = UnityChanState.Stand
		self.__renderer = {
			UnityChanState.Stand : UnityChanRenderer_Stand(),
			UnityChanState.Run : UnityChanRenderer_Run(),
			UnityChanState.Jump : UnityChanRenderer_Jump(),
		}

	def render(self):
		self.__renderer[self.__unity_chan_state].render()

	def stand(self): self.__unity_chan_state = UnityChanState.Stand
	def run(self):   self.__unity_chan_state = UnityChanState.Run
	def jump(self):  self.__unity_chan_state = UnityChanState.Jump

if __name__ == "__main__":

	view = UnityChanView()

	while True:
		view.render()

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

