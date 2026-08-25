import cv2

print("Starting camera...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not detected")
    exit()

print("Camera opened successfully")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Cannot read frame")
        break

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()