import cv2
import face_recognition
import os
import webbrowser

known_encodings = []
known_names = []

# Cargar imágenes de la carpeta "faces"
for filename in os.listdir("B:/python/projects/faces"):
    if filename.endswith(('.jpg', '.png')):
        image_path = os.path.join("B:/python/projects/faces", filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_encodings.append(encoding)
        known_names.append(os.path.splitext(filename)[0])

cap = cv2.VideoCapture(0)
recognized = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    face_locations = face_recognition.face_locations(frame)

    for face_location in face_locations:
        face_encoding = face_recognition.face_encodings(frame, [face_location])[0]
        matches = face_recognition.compare_faces(known_encodings, face_encoding)

        if True in matches:
            name = known_names[matches.index(True)]
            print(f"Reconocido: {name}")
            recognized = True
            break

    cv2.imshow("Reconocimiento Facial", frame)

    if recognized or cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Si reconoció a alguien, abre el HTML de éxito
if recognized:
    webbrowser.open('dashboard.html')
else:
    print("Acceso denegado")
