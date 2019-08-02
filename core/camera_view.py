import cv2
from detection_graph import DetectionObject
import time

class CameraView:
	def __init__(self):
		self.frame_count = 0
		self.fps = 0
		self.last_rendered_sec = int(time.time())
		self.shown = True
		self.display_results = True

	def draw_text(self, image, text, left, bottom):
		if self.display_results:
			cv2.putText(image, text, (left, bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), thickness=1)

	def draw_objects(self, image, objects):	
		if self.display_results:
			for obj in objects:
				y = obj.top
				if y < 10:
					y = 10
				self.draw_text(image, f"{obj.probability:.2f}", obj.left, y)
				cv2.rectangle(image, (obj.left, obj.top), (obj.right, obj.bottom), (0,255,0), 1)

	def draw_centroids(self, image, centroids_dict):	
		if self.display_results:
			# loop over the tracked objects
			for (objectID, centroid) in centroids_dict.items():
				# draw both the ID of the object and the centroid of the
				# object on the output image
				self.draw_text(image, f"ID {objectID}", centroid[0] - 10, centroid[1] - 10)
				cv2.circle(image, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

	def show(self, image):
		current_sec = int(time.time())
		if not self.last_rendered_sec == current_sec:
			self.last_rendered_sec = current_sec
			self.fps = self.frame_count
			self.frame_count = 0
		self.frame_count += 1

		self.draw_text(image, f"FPS : {self.fps}", 5, 15)
		
		cv2.imshow("hit q key to exit, d key to show/hide display info.", image)

		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			self.shown = False
			cv2.destroyAllWindows()
		elif key == ord('d'):
			self.display_results = not self.display_results
