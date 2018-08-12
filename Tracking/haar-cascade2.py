import cv2

# face_cascade = cv2.CascadeClassifier(
#     'venv\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')

# face_cascade = cv2.CascadeClassifier(
#     'samples\cascade\cascade_LBP.xml')

face_cascade = cv2.CascadeClassifier(
    # 'samples\cascade\cascade_LBP.xml')
    'samples\cascade\cascade.xml')

# eye_cascade = cv2.CascadeClassifier(
#     'venv\Lib\site-packages\cv2\data\haarcascade_eye.xml')

cap = cv2.VideoCapture("samples/2.avi")
# cap = cv2.VideoCapture("samples/airplane.mp4")
# cap = cv2.VideoCapture(0)

# Take first frame and find corners in it
# ret, frame = cap.read()


while True:
    # Start timer
    timer = cv2.getTickCount()

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex, ey, ew, eh) in eyes:
        #     cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0),
        #                   2)

    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    # Display FPS on frame
    cv2.putText(frame, "FPS : " + str(int(fps)), (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
