#Este codigo cuenta con un error, debido a que si yo estoy solo
#me detecta sin problemas, caso contrario
#si coloco a otra persona a la vez, me marca desconocido tanto para mi como a la otra persona

import cv2
import face_recognition

# Cargar imagen de referencia
image = cv2.imread("C:/Python/pruebasMaestria/proyectoMaestria/9.-sistemasDeVisionArtificial/3er.- parcial/faceID2/images/jesus.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
face_loc = face_recognition.face_locations(image)[0]
face_image_encodings = face_recognition.face_encodings(image, known_face_locations=[face_loc])[0]

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    if frame_count % 5 == 0:
        face_locations = face_recognition.face_locations(small_frame, model="hog")

    for face_location in face_locations:
        top, right, bottom, left = [x * 2 for x in face_location]
        if frame_count % 5 == 0:
            face_frame_encodings = \
            face_recognition.face_encodings(frame, known_face_locations=[(top, right, bottom, left)])[0]
            result = face_recognition.compare_faces([face_image_encodings], face_frame_encodings)

        text, color = ("Rodrigo", (125, 220, 0)) if result[0] else ("Desconocido", (50, 50, 255))
        cv2.rectangle(frame, (left, bottom), (right, bottom + 30), color, -1)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, text, (left, bottom + 20), 2, 0.7, (254, 253, 252), 1)

    cv2.imshow("Frame", frame)
    frame_count += 1
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
