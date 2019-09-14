import os
import cv2
import time
import config
from core.unity_chan.unity_chan import UnityChanView


class TrackingView:
    def __init__(self, width, height):
        self.frame_count = 0
        self.fps = 0
        self.last_rendered_sec = int(time.time())
        self.display_results = True

        self.people_count = 0
        self.pass_count = 0

        self.width = width
        self.height = height
        self.shown = True
        self.image = None

        self.blank_display = True
        self.blank_image = None

        self.unity_chan = True
        self.unity_chan_view = UnityChanView()

        if os.path.exists("pastconunt.txt"):
            fp = open("pastconunt.txt", "r")
            content = fp.read()
            tokens = content.split(",")
            self.past_people_count = int(tokens[0])
            self.past_pass_count = int(tokens[1])

            fp.close()
        else:
            self.past_people_count = 0
            self.past_pass_count = 0

    def save(self):
        fp = open("pastconunt.txt", "w")
        fp.write(f"{self.people_count + self.past_people_count},"
                 f"{self.pass_count + self.past_pass_count}")
        fp.close()

    def __draw_text(self,
                    image,
                    text,
                    left,
                    bottom,
                    text_color=config.TEXT_COLOR,
                    bgcolor=config.TEXT_BGCOLOR,
                    scale=0.7,
                    thickness=2):
        if self.display_results:
            margin = 2
            (label_width, label_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
            cv2.rectangle(image, (left, bottom - label_height - margin * 2), (left + label_width + margin * 2, bottom), bgcolor, cv2.FILLED)
            cv2.putText(image, text, (left + margin, bottom - margin - 1), cv2.FONT_HERSHEY_SIMPLEX, scale, text_color, thickness=thickness)

    def set_image(self, image):
        self.image = image

        if self.blank_display:
            if self.blank_image is None:
                self.blank_image = cv2.imread("core/image/blank.png")
                self.blank_image = cv2.resize(self.blank_image, (self.width, self.height))

                self.blank_image_for_counter = cv2.resize(self.blank_image, (900, 100))
            self.image = self.blank_image.copy()

        return self

    def draw_objects(self, objects):
        if self.display_results:
            for obj in objects:

                # not to break throught the window upper edge...
                y = obj.top
                if y < 10:
                    y = 10

                if self.unity_chan:
                    unity_chan_x = int((obj.left + obj.right) / 2)
                    unity_chan_y = int((obj.top + obj.bottom) / 2)
                    unity_chan_size = int((obj.bottom - obj.top) * 1.1)
                    # print(f"Unity-Chan size : {unity_chan_size}")
                    self.unity_chan_view.render(self.image, unity_chan_x, unity_chan_y, unity_chan_size, unity_chan_size)
                else:
                    self.__draw_text(self.image, f"{obj.probability:.2f}", obj.left, y, bgcolor=config.COLOR_ORANGE)
                    cv2.rectangle(self.image, (obj.left, obj.top), (obj.right, obj.bottom), config.COLOR_ORANGE, 1)

        return self

    def draw_centroids(self, tracking_objects_dict):
        latest_point_color = config.COLOR_ORANGE
        oldest_point_color = config.COLOR_YELLOW
        color_diff = (
            latest_point_color[0] - oldest_point_color[0],
            latest_point_color[1] - oldest_point_color[1],
            latest_point_color[2] - oldest_point_color[2]
        )

        if self.display_results:
            for (objectID, tracking_object) in tracking_objects_dict.items():

                # found new object id. i.e. new person was found.
                if self.people_count < objectID:
                    self.people_count = objectID

                if tracking_object.passed() and not tracking_object.was_counted():
                    self.pass_count += 1
                    tracking_object.mark_as_counted()

                if tracking_object.is_lost:
                    obj_status = f"lost {tracking_object.lost_frame_count}"
                else:
                    obj_status = f"tracking {tracking_object.tracking_frame_count}"

                # make subclass to show unity chan's text
                if self.unity_chan:
                    xx = tracking_object.centroid.x + 50
                else:
                    xx = tracking_object.centroid.x - 10

                self.__draw_text(self.image, f"ID {objectID}, {obj_status}", xx, tracking_object.centroid.y - 10, bgcolor=config.COLOR_ORANGE)

                last_point = None
                footprint_count = len(tracking_object.footprints)

                for i, point in enumerate(tracking_object.footprints):

                    # make gradiation on showing history
                    if footprint_count > 1:
                        color_step = i / (footprint_count - 1)
                        color = (
                            int(oldest_point_color[0] + color_diff[0] * color_step),
                            int(oldest_point_color[1] + color_diff[1] * color_step),
                            int(oldest_point_color[2] + color_diff[2] * color_step),
                        )
                    else:
                        color = latest_point_color

                    if i > 0:
                        cv2.line(self.image, (last_point.x, last_point.y), (point.x, point.y), color, 2)

                    if config.VERBOSE_LOG:
                        print(f"{i} : {point.x} { point.y}")

                    cv2.circle(self.image, (point.x, point.y), 4, color, -1)
                    last_point = point

        return self

    def show(self):
        current_sec = int(time.time())
        if not self.last_rendered_sec == current_sec:
            self.last_rendered_sec = current_sec
            self.fps = self.frame_count
            self.frame_count = 0
        self.frame_count += 1

        self.__draw_text(self.image, f"COUNT : {self.people_count + self.past_people_count}", 5, 20)
        self.__draw_text(self.image, f"PASS : {self.pass_count + self.past_pass_count}", 5, 40)
        self.__draw_text(self.image, f"FPS : {self.fps}", 5, 60)

        counter_view = self.blank_image_for_counter.copy()
        self.__draw_text(counter_view, f"COUNT : {self.people_count + self.past_people_count}", 5, 95, scale = 4, text_color = (255, 255, 255), bgcolor = (0, 0, 0), thickness=4)

        # cv2.line(self.image, (config.PASS_COUNT_LEFT_BORDER, 0), (config.PASS_COUNT_LEFT_BORDER, self.height), (255, 0, 0), 2)
        # cv2.line(self.image, (config.PASS_COUNT_RIGHT_BORDER, 0), (config.PASS_COUNT_RIGHT_BORDER, self.height), (255, 0, 0), 2)

        cv2.imshow("hit q key to exit, c key to show/hide camera image, d key to show/hide display info.", self.image)
        cv2.imshow("count", counter_view)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.shown = False
            cv2.destroyAllWindows()
            print("exit")

        # todo : make display mode.
        elif key == ord('c'):
            self.blank_display = not self.blank_display
        elif key == ord('d'):
            self.display_results = not self.display_results
        elif key == ord('u'):
            self.unity_chan = not self.unity_chan

        return self
