import cv2,time
def display_frames_per_second(frame, start_time):
	END_TIME = abs(start_time-time.time())
	TOP_LEFT = (0,0)
	BOTTOM_RIGHT = (116,26)
	TEXT_POSITION = (8,20)
	TEXT_SIZE = 0.6
	FONT = cv2.FONT_HERSHEY_SIMPLEX
	COLOR = (255,255,0) #BGR
	cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0,0,0), cv2.FILLED)
	cv2.putText(frame, "FPS: {}".format(round(1/max(0.0333,END_TIME),1)), TEXT_POSITION, FONT, TEXT_SIZE,COLOR)
	return frame