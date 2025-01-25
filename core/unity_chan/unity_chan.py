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
        dir = os.path.abspath(os.path.dirname(__file__))
        self.img_path = os.path.join(dir, "image")

    def get_image_index(self):
        return self.rendering_count % len(self.unity_chan_image)

    # def render(self, base_image, x, y, unity_chan_width, unity_chan_height):

    #     # print(f"rendering count : {self.rendering_count}")

    #     idx = self.get_image_index()

    #     base_height, base_width, base_depth = base_image.shape

    #     xx = x - int(unity_chan_width / 2)
    #     if xx < 0:
    #         xx = 0
    #     if xx + unity_chan_width > base_width:
    #         xx -= xx + unity_chan_width - base_width

    #     yy = y - int(unity_chan_height / 2)
    #     if yy < 0:
    #         yy = 0
    #     if yy + unity_chan_height > base_height:
    #         yy -= yy + unity_chan_height - base_height

    #     resized = cv2.resize(
    #         self.unity_chan_image[idx],
    #         (unity_chan_width, unity_chan_height)
    #     )
    #     base_image[yy:yy+unity_chan_height, xx:xx+unity_chan_width] = resized

    #     self.rendering_count += 1

    def render(self, base_image, x, y, unity_chan_width, unity_chan_height):
        # print(f"rendering count : {self.rendering_count}")

        idx = self.get_image_index()
        base_height, base_width, base_depth = base_image.shape

        xx = x - int(unity_chan_width / 2)
        if xx < 0:
            xx = 0
        if xx + unity_chan_width > base_width:
            xx -= xx + unity_chan_width - base_width

        yy = y - int(unity_chan_height / 2)
        if yy < 0:
            yy = 0
        if yy + unity_chan_height > base_height:
            yy -= yy + unity_chan_height - base_height

        # Adjust the height and width to fit within the base image
        cropped_height = min(unity_chan_height, base_height - yy)
        cropped_width = min(unity_chan_width, base_width - xx)

        # Resize the image to the adjusted dimensions
        resized = cv2.resize(
            self.unity_chan_image[idx],
            (cropped_width, cropped_height)
        )

        try:
            # Only replace the portion that fits within the base image
            base_image[yy:yy+cropped_height, xx:xx+cropped_width] = resized
        except Exception as e:
            print(f"Error: {e}")
            print(f"yy: {yy}, yy+cropped_height: {yy+cropped_height}, xx: {xx}, xx+cropped_width: {xx+cropped_width}")
            print(f"x: {x}, y: {y}, unity_chan_width: {unity_chan_width}, unity_chan_height: {unity_chan_height}")

        self.rendering_count += 1

class UnityChanRenderer_Stand(UnityChanRenderer):
    def __init__(self):
        super().__init__()

        self.unity_chan_image = [
            cv2.imread(os.path.join(self.img_path, "stand_1.png")),
            cv2.imread(os.path.join(self.img_path, "stand_2.png")),
            cv2.imread(os.path.join(self.img_path, "stand_3.png")),
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

        self.unity_chan_image = [
            cv2.imread(os.path.join(self.img_path, "run_1.png")),
            cv2.imread(os.path.join(self.img_path, "run_2.png")),
            cv2.imread(os.path.join(self.img_path, "run_3.png")),
            cv2.imread(os.path.join(self.img_path, "run_4.png")),
            cv2.imread(os.path.join(self.img_path, "run_5.png")),
            cv2.imread(os.path.join(self.img_path, "run_6.png")),
            cv2.imread(os.path.join(self.img_path, "run_7.png")),
            cv2.imread(os.path.join(self.img_path, "run_8.png")),
        ]


class UnityChanRenderer_Jump(UnityChanRenderer):
    def __init__(self):
        super().__init__()

        self.unity_chan_image = [
            cv2.imread(os.path.join(self.img_path, "jump_1.png")),
            cv2.imread(os.path.join(self.img_path, "jump_2.png")),
            cv2.imread(os.path.join(self.img_path, "jump_3.png")),
            cv2.imread(os.path.join(self.img_path, "jump_4.png")),
            cv2.imread(os.path.join(self.img_path, "jump_5.png")),
            cv2.imread(os.path.join(self.img_path, "jump_6.png")),
            cv2.imread(os.path.join(self.img_path, "jump_7.png")),
        ]


class UnityChanView:
    def __init__(self):
        self.__unity_chan_state = UnityChanState.Run
        self.__renderer = {
            UnityChanState.Stand: UnityChanRenderer_Stand(),
            UnityChanState.Run: UnityChanRenderer_Run(),
            UnityChanState.Jump: UnityChanRenderer_Jump(),
        }

    def render(self, base_image, x, y, unity_chan_width, unity_chan_height):
        self.__renderer[self.__unity_chan_state].render(
            base_image, x, y, unity_chan_width, unity_chan_height
        )

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
            cv2.destroyAllWindows()
            print("exit")
        elif key == ord('a'):
            view.run()
        elif key == ord('s'):
            view.stand()
        elif key == ord(' '):
            view.jump()
