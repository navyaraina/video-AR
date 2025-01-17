import numpy as np
import cv2
CACHED_REF_PTS = None

def find_and_warp(frame, source, cornerIDs, arucoDict, arucoParams, useCache=False):
	global CACHED_REF_PTS
	
	(imgH, imgW) = frame.shape[:2]
	(srcH, srcW) = source.shape[:2]
	(corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
	ids = np.array([]) if len(corners) != 4 else ids.flatten()
	refPts = []
	for i in cornerIDs:
        
		j = np.squeeze(np.where(ids == i))
		if j.size == 0:
			continue
		corner = np.squeeze(corners[j])
		refPts.append(corner)
	if len(refPts) != 4:
		
		if useCache and CACHED_REF_PTS is not None:
			refPts = CACHED_REF_PTS
		
		else:
			return None
	
	if useCache:
		CACHED_REF_PTS = refPts
	(refPtTL, refPtTR, refPtBR, refPtBL) = refPts
	dstMat = [refPtTL[0], refPtTR[1], refPtBR[2], refPtBL[3]]
	dstMat = np.array(dstMat)
	
	srcMat = np.array([[0, 0], [srcW, 0], [srcW, srcH], [0, srcH]])
	
	(H, _) = cv2.findHomography(srcMat, dstMat)
	warped = cv2.warpPerspective(source, H, (imgW, imgH))
	mask = np.zeros((imgH, imgW), dtype="uint8")
	cv2.fillConvexPoly(mask, dstMat.astype("int32"), (255, 255, 255), cv2.LINE_AA)
	
	rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
	mask = cv2.dilate(mask, rect, iterations=2)
	
	maskScaled = mask.copy() / 255.0
	maskScaled = np.dstack([maskScaled] * 3)
	warpedMultiplied = cv2.multiply(warped.astype("float"),
		maskScaled)
	imageMultiplied = cv2.multiply(frame.astype(float),
		1.0 - maskScaled)
	output = cv2.add(warpedMultiplied, imageMultiplied)
	output = output.astype("uint8")
	
	return output