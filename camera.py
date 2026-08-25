import cv2

# Open the default webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read a frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Show the frame
    cv2.imshow("Smart Crowd Camera", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera
cap.release()
cv2.destroyAllWindows()