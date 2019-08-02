import cv2
from detection_graph import DetectionObject
import time
import config

class TrackingView:
	def __init__(self, width, height):
		self.frame_count = 0
		self.fps = 0
		self.last_rendered_sec = int(time.time())
		self.shown = True
		self.display_results = True
		self.people_count = 0
		self.width = width
		self.height = height

	def draw_text(self, image, text, left, bottom, text_color = config.TEXT_COLOR, bgcolor = config.TEXT_BGCOLOR):
		if self.display_results:
			margin = 2
			(label_width, label_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
			cv2.rectangle(image, (left, bottom - label_height - margin * 2), (left + label_width + margin * 2, bottom), bgcolor, cv2.FILLED)
			cv2.putText(image, text, (left + margin, bottom - margin - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, thickness=1)

	def draw_objects(self, image, objects):	
		if self.display_results:
			for obj in objects:

				# not to break throught the window upper edge...
				y = obj.top
				if y < 10:
					y = 10

				self.draw_text(image, f"{obj.probability:.2f}", obj.left, y, bgcolor=config.COLOR_ORANGE)
				cv2.rectangle(image, (obj.left, obj.top), (obj.right, obj.bottom), config.COLOR_ORANGE, 1)

	def draw_centroids(self, image, tracking_objects_dict):
		latest_point_color = config.COLOR_ORANGE
		oldest_point_color = config.COLOR_YELLOW
		color_diff = (
			latest_point_color[0] - oldest_point_color[0],
			latest_point_color[1] - oldest_point_color[1],
			latest_point_color[2] - oldest_point_color[2]
		)

		if self.display_results:
			for (objectID, tracking_object) in tracking_objects_dict.items():
				if tracking_object.passed() and not tracking_object.was_counted():
					self.people_count += 1
					tracking_object.mark_as_counted()

				if tracking_object.is_lost:
					obj_status = f"lost {tracking_object.lost_frame_count}"
				else:
					obj_status = f"tracking {tracking_object.tracking_frame_count}"

				self.draw_text(image, f"ID {objectID}, {obj_status}", tracking_object.centroid.x - 10, tracking_object.centroid.y - 10, bgcolor=config.COLOR_ORANGE)

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
						cv2.line(image, (last_point.x, last_point.y), (point.x, point.y), color, 2)

					if config.VERBOSE_LOG:
						print(f"{i} : {point.x} { point.y}")

					cv2.circle(image, (point.x, point.y), 4, color, -1)
					last_point = point

	def show(self, image):
		current_sec = int(time.time())
		if not self.last_rendered_sec == current_sec:
			self.last_rendered_sec = current_sec
			self.fps = self.frame_count
			self.frame_count = 0
		self.frame_count += 1

		self.draw_text(image, f"FPS : {self.fps}", 5, 15)
		self.draw_text(image, f"COUNT : {self.people_count}", 5, 30)

		# cv2.line(image, (config.PEOPLE_COUNT_LEFT_BORDER, 0), (config.PEOPLE_COUNT_LEFT_BORDER, self.height), (255, 0, 0), 2)
		# cv2.line(image, (config.PEOPLE_COUNT_RIGHT_BORDER, 0), (config.PEOPLE_COUNT_RIGHT_BORDER, self.height), (255, 0, 0), 2)
		
		cv2.imshow("hit q key to exit, d key to show/hide display info.", image)

		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			self.shown = False
			cv2.destroyAllWindows()
			print("exit")
		elif key == ord('d'):
			self.display_results = not self.display_results
