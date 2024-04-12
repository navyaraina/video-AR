from pyimagesearch.augmented_reality import find_and_warp
from imutils.video import VideoStream
from collections import deque
import argparse
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, required=True,
	help="path to input video file for augmented reality")
ap.add_argument("-c", "--cache", type=int, default=-1,
	help="whether or not to use reference points cache")
args = vars(ap.parse_args())

print("[INFO] initializing marker detector...")
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
arucoParams = cv2.aruco.DetectorParameters_create()

print("[INFO] accessing video stream...")
vf = cv2.VideoCapture(args["input"])

Q = deque(maxlen=128)

(grabbed, source) = vf.read()
Q.appendleft(source)

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

while len(Q) > 0:
    frame = vs.read()
    frame = imutils.resize(frame, width=1200)
	
    warped = find_and_warp(frame, source, cornerIDs=(923, 1001, 241, 1007), arucoDict=arucoDict, arucoParams=arucoParams, useCache=args["cache"] > 0)
    
    if warped is not None:
		
    	frame = warped
    	source = Q.popleft()
	
    if len(Q) != Q.maxlen:
        (grabbed, nextFrame) = vf.read()
    if grabbed:
    	Q.append(nextFrame)       
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
	
    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()