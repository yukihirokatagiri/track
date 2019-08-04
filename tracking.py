import sys
import config
import time
import cv2

print(f"Loading {config.MODEL_PATH}")

# tensorflow object detection API
# Check your PYTHONPATH if failed to import this.
from object_detection.utils import label_map_util

sys.path.insert(0, "core")
from detection_graph import Detector
from centroid_tracker import CentroidTracker
from centroid_tracker import TrackingObject
from camera import *
from tracking_view import TrackingView

def get_image_stream():
	if not config.INPUT_FILE == "":
		stream = FileStream()
		print("FileStream")
	else:
		stream = Camera()
		print(f"Camera {config.CAMERA_ID}")

	return stream

def quit(msg):
	print(msg)
	sys.exit()

def main():
	stream = get_image_stream()
	stream.open()
	frame = stream.read()
	if frame is None:
		quit("Failed to load stream.")

	height, width, depth = frame.shape

	if config.VERBOSE_LOG:
		print(f"Width : {width}, Height : {height}")

	tracking_view = TrackingView(width, height)

	detector = Detector()

	loaded = detector.load(config.MODEL_PATH)
	if not loaded:
		quit(f"Failed to load model : {config.MODEL_PATH}")

	tracker = CentroidTracker()

	lables = label_map_util.create_category_index_from_labelmap(config.LABEL_PATH, use_display_name=True)

	if config.VERBOSE_LOG:
		print(lables)

	while stream.isOpened() and tracking_view.shown:
		frame = stream.read()
		if frame is None:
			quit("Failed to read image.")

		t = time.time()

		objects = detector.detect(frame)

		if config.VERBOSE_LOG:
			print(f"detect : {time.time() - t:.2f}")

		centroids_dict = tracker.update(objects)

		# show result
		tracking_view.set_image(frame)\
						.draw_objects(objects)\
						.draw_centroids(centroids_dict)\
						.show()

	stream.close()

if __name__== "__main__":
	main()
