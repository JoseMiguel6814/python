import cv2
cap = cv2.VideoCapture(0)  # Prueba con otros índices si no funciona
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
