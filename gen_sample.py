from object_detection.utils import visualization_utils as vis_util
import numpy as np
import cv2


w = 640
h = 480
frame = np.zeros((h, w, 3), dtype=np.uint8)
boxes = np.array(
    [(0, 0, .1, .1),
     (0, 0, .2, .2),
     (0, 0, .3, .3),
     (0, 0, .4, .4)]
)
classes = np.array(
    [1, 2, 3, 4], dtype=np.int32
)
scores = np.array([.8] * 4)
vis_util.visualize_boxes_and_labels_on_image_array(
	frame,
	boxes,
	classes,
	scores,
	{1: {'id': 1, 'name': 'armature'},
	 2: {'id': 2, 'name': 'rock'},
	 3: {'id': 3, 'name': 'wood'},
	 4: {'id': 4, 'name': 'other'}},
	min_score_thresh=0.5,
	use_normalized_coordinates=True,
	line_thickness=8
)
cv2.imwrite('sample.png', frame)	