import os
import argparse

# defaults
DEF_MODEL_PATH = "D:/12_ML/07_pretrained_models//ssdlite_mobilenet_v2_coco_2018_05_09.pb"	# pre-trained model file
DEF_LABEL_PATH = "label/mscoco_label_map.pbtxt"								# label definiction file  
DEF_CONFIDENCE = 0.5
DEF_CAMERA_ID = 0
DEF_VERBOSE_LOG = False
DEF_TARGET_CLASS = 1 # detect people
DEF_LOST_FRAME = 50
DEF_TRACKING_HISTORY = 10

# argument description
parser_cfg = argparse.ArgumentParser()
parser_cfg.add_argument('--model', dest='model', default=DEF_MODEL_PATH, help='trained model path')
parser_cfg.add_argument('--lalel', dest='label', default=DEF_LABEL_PATH, help='label definition file path')
parser_cfg.add_argument('--confidence', dest='confidence', default=DEF_CONFIDENCE, help='minmum score of the detection probability')

# todo use 'choice' option
parser_cfg.add_argument('--camera_id', dest='camera_id', default=DEF_CAMERA_ID, help='camera id')
parser_cfg.add_argument('--input_file', '-i', dest='input_file', default="", help='class id to be detected')
parser_cfg.add_argument('--staic_image', dest='staic_image', default="core/image/blank.png", help='class id to be detected')

parser_cfg.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='print verbose log if True')
parser_cfg.add_argument('--target', dest='target', default=DEF_TARGET_CLASS, help='class id to be detected')
# parser_cfg.add_argument('--all', '-a', dest='all', action='store_true', help='run all')
parser_cfg.add_argument('--lost_frame', dest='lost_frame', default=DEF_LOST_FRAME, help='remove tracking point if the object keeps disappeared on the frame count')
parser_cfg.add_argument('--history', type=int, dest='history', default=DEF_TRACKING_HISTORY, help='tracking history')

# read arguments
args_cfg = parser_cfg.parse_args()
MODEL_PATH = args_cfg.model
LABEL_PATH = args_cfg.label
CONFIDENCE = args_cfg.confidence
CAMERA_ID = args_cfg.camera_id
VERBOSE_LOG = args_cfg.verbose
TARGET_CLASS = args_cfg.target
INPUT_FILE = args_cfg.input_file
STATIC_IMAGE = args_cfg.staic_image
# RUN_ALL = args_cfg.all
LOST_COUNT = args_cfg.lost_frame
TRACKING_HISTORY = args_cfg.history

COLOR_ORANGE = (24, 89, 207) # blue, green, red
COLOR_YELLOW = (90, 203, 246) # blue, green, red
TEXT_COLOR = (32, 32, 32) # blue, green, red
TEXT_BGCOLOR = (0, 255, 127) # blue, green, red

PASS_COUNT_LEFT_BORDER = 250
PASS_COUNT_RIGHT_BORDER = 390

# debug print
if VERBOSE_LOG:
	print("Config")
	print(f"\tMODEL_PATH : {MODEL_PATH}")
	print(f"\tLABEL_PATH : {LABEL_PATH}")
	print(f"\tCONFIDENCE : {CONFIDENCE}")
	print(f"\tCAMERA_ID : {CAMERA_ID}")
	print(f"\tVERBOSE_LOG : {VERBOSE_LOG}")
	print(f"\tTARGET_CLASS : {TARGET_CLASS}")
	print(f"\tINPUT_FILE : {INPUT_FILE}")
	# print(f"\tRUN_ALL : {RUN_ALL}")
	print(f"\tLOST_COUNT : {LOST_COUNT}")
	print(f"\tTRACKING_HISTORY : {TRACKING_HISTORY}")

# pretrained_models = {
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_inception_resnet_v2_atrous_coco_11_06_2017.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid_2018_01_28.pb" : "label/oid_v4_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_inception_v2_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_nas_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet101_ava_v2.1_2018_04_30.pb" : "label/ava_label_map_v2.1.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet101_coco_11_06_2017.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet101_kitti_2018_01_28.pb" : "label/kitti_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet101_lowproposals_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet50_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//faster_rcnn_resnet50_lowproposals_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//mask_rcnn_inception_v2_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//mask_rcnn_resnet50_atrous_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",
# 	"D:/12_ML/07_pretrained_models//rfcn_resnet101_coco_11_06_2017.pb" : "label/mscoco_label_map.pbtxt",

# 	# 15 fps
# 	"D:/12_ML/07_pretrained_models//ssdlite_mobilenet_v2_coco_2018_05_09.pb" : "label/mscoco_label_map.pbtxt",

# 	# 13 fps
# 	"D:/12_ML/07_pretrained_models//ssd_inception_v2_coco_11_06_2017.pb" : "label/mscoco_label_map.pbtxt",

# 	# 15 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v1_0.75_depth_300x300_coco14_sync_2018_07_03.pb" : "label/mscoco_label_map.pbtxt",

# 	# 11 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v1_coco_2017_11_17.pb" : "label/mscoco_label_map.pbtxt",

# 	# 15 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v1_coco_2018_01_28.pb" : "label/mscoco_label_map.pbtxt",

# 	# 8 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03.pb" : "label/mscoco_label_map.pbtxt",

# 	# 14 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v1_ppn_shared_box_predictor_300x300_coco14_sync_2018_07_03.pb" : "label/mscoco_label_map.pbtxt",

# 	# 14 fps
# 	"D:/12_ML/07_pretrained_models//ssd_mobilenet_v2_coco_2018_03_29.pb" : "label/mscoco_label_map.pbtxt",

# 	# 7 fps
# 	"D:/12_ML/07_pretrained_models//ssd_resnet50_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03.pb" : "label/mscoco_label_map.pbtxt",
# }
