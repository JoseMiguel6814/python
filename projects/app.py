from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import face_recognition
import cv2
import numpy as np
import base64
import os
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = "clave_super_secreta"


CORS(app)
# Cargar rostros conocidos
known_faces = []
known_names = []

faces_folder = "B:/python/projects/faces"
for filename in os.listdir(faces_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        name = os.path.splitext(filename)[0]
        image_path = os.path.join(faces_folder, filename)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(name)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login_face", methods=["POST"])
def login_face():
    data = request.get_json()
    image_data = data["image"].split(",")[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    face_locations = face_recognition.face_locations(frame)
    if face_locations:
        face_enc = face_recognition.face_encodings(frame, known_face_locations=face_locations)[0]
        results = face_recognition.compare_faces(known_faces, face_enc)
        if True in results:
            index = results.index(True)
            name = known_names[index]
            session["user"] = name
            return jsonify({"success": True, "name": name})
    session["user"] = "desconocido"
    return jsonify({"success": False})

@app.route("/dashboard")
def dashboard():
    name = session.get("user", "desconocido")
    return render_template("dashboard.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)
