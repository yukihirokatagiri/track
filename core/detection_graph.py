import tensorflow as tf
import config
import numpy as np


class DetectionObject:
    def __init__(self, left, top, right, bottom, class_id, probability):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.class_id = class_id
        self.probability = probability


class Detector:
    def __init__(self):
        self.g = None
        self.session = None
        self.image_tensor = None
        self.detection_boxes = None
        self.detection_scores = None
        self.detection_classes = None
        self.num_detections = None

    def load(self, graph_file_path):
        ret = False

        detection_graph = tf.Graph()
        with detection_graph.as_default():

            # GraphDef can load serialzied graph, such as pretrained model data.
            # We import specified graph here with tf.import_graph_def function.
            graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(graph_file_path, 'rb') as fid:
                serialized_graph = fid.read()
                graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(graph_def, name='')

            self.session = tf.compat.v1.Session(graph=detection_graph) 
            self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            ret = True

        return ret

    def detect(self, image):
        height, width, depth = image.shape
        image_np_expanded = np.expand_dims(image, axis=0)

        param_array = [
            self.detection_boxes,
            self.detection_scores,
            self.detection_classes,
            self.num_detections
        ]
        (boxes, scores, classes, num) = self.session.run(param_array, feed_dict={self.image_tensor: image_np_expanded})

        objects = []

        idx = 0
        for score in scores[0]:
            if score > config.CONFIDENCE:
                class_id = classes[0][idx]
                if class_id == config.TARGET_CLASS:
                    ymin = boxes[0][idx][0]
                    xmin = boxes[0][idx][1]
                    ymax = boxes[0][idx][2]
                    xmax = boxes[0][idx][3]

                    (left, top, right, bottom) = (
                        int(xmin * width), 
                        int(ymin * height), 
                        int(xmax * width),
                        int(ymax * height)
                    )

                    objects.append(DetectionObject(left, top, right, bottom, class_id, score))
                    idx += 1
                else:
                    pass
            else:
                break

        if config.VERBOSE_LOG:
            for obj in objects:
                print(f"({obj.left}, {obj.top}), ({obj.right}, {obj.bottom}), class : {obj.class_id}, probability : {obj.probability}")

        return objects
