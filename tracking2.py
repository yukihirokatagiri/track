# from ultralytics import YOLO

# if __name__ == '__main__':
#     # Load a model
#     print("Loading yolov8n.pt")
#     model = YOLO('yolov8n.pt')
#     print("Loaded yolov8n.pt")

#     # Predict the model
#     model.predict('https://ultralytics.com/images/bus.jpg', save=True, conf=0.5)
#     print("Predicted yolov8n.pt")
from ultralytics import YOLO
import cv2
from core.centroid_tracker import CentroidTracker
from core.tracking_view import TrackingView

class Box:
    def __init__(self):
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.name = None
        self.object_id = None
        self.probability = None

if __name__ == '__main__':
    # Load a model
    print("Loading yolo11n.pt")
    model = YOLO('yolo11n.pt')
    print("Loaded yolo11n.pt")

    # Initialize webcam
    cap = cv2.VideoCapture(0)  # 0 is the default webcam, change if needed

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Webcam opened. Press 'q' to quit.")

    tracker = CentroidTracker()

    # Read the webcam to get the frame
    ret, frame = cap.read()
    height, width = frame.shape[:2]
    tracking_view = TrackingView(width, height)

    # Get 'person' class ID of the model
    person_id = [k for k, v in model.names.items() if v == 'person'][0]  # Get 'person' class ID

    while tracking_view.shown:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Predict with YOLO
        # https://docs.ultralytics.com/modes/predict/#inference-arguments
        results = model.predict(source=frame, conf=0.5, save=False, show=False)
        person_boxes = [box for box in results[0].boxes if int(box.cls) == person_id]

        boxes = []
        for box in person_boxes:
            b = Box()
            b.left, b.top, b.right, b.bottom = map(int, box.xyxy[0])  # Bounding box coordinates
            b.name = model.names[int(box.cls)]  # Class name
            b.object_id = int(box.cls)  # Class ID
            b.probability = float(box.conf[0])  # Confidence score
            boxes.append(b)

        # Annotate frame with predictions
        # annotated_frame = results[0].plot()  # Plot detections on the frame

        # Display the annotated frame
        # cv2.imshow('YOLOv8 Webcam', annotated_frame)

        # # Break loop on 'q' key press
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        centroids_dict = tracker.update(boxes)

        # show result
        tracking_view.set_image(frame)\
                     .draw_objects(boxes)\
                     .draw_centroids(centroids_dict)\
                     .show()

    # Release webcam and close windows
    cap.release()
    cv2.destroyAllWindows()
    tracking_view.save()