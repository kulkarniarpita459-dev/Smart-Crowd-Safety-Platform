import cv2

VIDEO_PATH = r"C:\Users\sande\indianfestival.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

print("Opened:", cap.isOpened())

if cap.isOpened():

    ret, frame = cap.read()

    print("Frame read:", ret)

    if ret:
        print("Video is working correctly.")

        cv2.imshow("Test Video", frame)
        cv2.waitKey(0)

    cap.release()

cv2.destroyAllWindows()