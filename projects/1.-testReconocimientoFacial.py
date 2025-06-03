#Aqui padrino, para poder usar face_recognition se debe hacer lo siguiente
'''
1.- Descargar visual studio (el moradito, el azul no)
2.- Instalar los modulos de desarrollo para escritorio con C++
    Ahí viene el CMake, que son dependencias DLL para poder usar el face recognition
3.- Terminada la instalación, instalar desde la terminal de python cmake
    pip install cmake
4.- Una vez terminado eso, instalar dlib
    pip install dlib
5.- terminando eso, instalar las siguientes librerias
    pip install face-recognition
    pip install opencv-contrib-python
'''

import cv2
import face_recognition


image = cv2.imread("C:/python/projects/images/yo.jpg")
face_loc = face_recognition.face_locations(image)[0]
#print("localización de rostros: ", face_loc)

face_image_encodings = face_recognition.face_encodings(image, known_face_locations=[face_loc])[0]
#print("codificación de rostros: ", face_image_encodings)

#cv2.rectangle(image, (face_loc[3], face_loc[0]), (face_loc[1], face_loc[2]), (0, 255, 0))
#cv2.imshow("Image", image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


######################################################################################
# Video Streaming
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
while True:
     ret, frame = cap.read()
     if ret == False: break
     frame = cv2.flip(frame, 1)
     face_locations = face_recognition.face_locations(frame)
     if face_locations != []:
          for face_location in face_locations:
               face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
               #En esta linea se hacer la comparación papito, la imagen de entrada al inicio si es igual
               #a la que la camara ve, el resultado debe de ser TRUE, caso contrario, FALSE
               #Que significa que no el mismo individuo
               result = face_recognition.compare_faces([face_image_encodings], face_frame_encodings)
               print("Result:", result)

               '''
                    Hata este punto correr el código y mostrar el rostro que se coloco en la imagen de entrada
                    y a su vez calar con otro rostro y ver que marque TRUE cuando sea el mismo rostro
                    y False cuando sea un rostro diferente
               '''

               #if result[0] == True:
                    #text = "Gaby"
                    #color = (125, 220, 0)
               #else:
                    #text = "Desconocido"
                    #color = (50, 50, 255)
               #cv2.rectangle(frame, (face_location[3], face_location[2]), (face_location[1], face_location[2] + 30), color, -1)
               #cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)

               cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), (0, 255, 0), 2)
     cv2.imshow("Frame", frame)
     k = cv2.waitKey(1)
     if k == 27 & 0xFF:
         break
cap.release()
cv2.destroyAllWindows()

