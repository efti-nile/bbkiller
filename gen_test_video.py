import cv2


length = 200  # frames
frame = cv2.imread('data\\conv_00-36-26_F38.png')
h, w, _ = frame.shape

fourcc = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter('data\\test_video.avi', fourcc, 20.0, (w, h))
for _ in range(length):
    output.write(frame)
output.release()
