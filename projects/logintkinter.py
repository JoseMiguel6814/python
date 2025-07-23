from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import face_recognition
import cv2
import numpy as np
import base64
import os
import random
from flask_cors import CORS
from datetime import datetime
import threading
import time

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

# Estado del sistema domótico
domotic_state = {
    "humedad": {
        "valor": 45,
        "unidad": "%",
        "estado_servo": False,
        "historico": []
    },
    "temperatura": {
        "valor": 25,
        "unidad": "°C",
        "alerta": False,
        "historico": []
    },
    "cuarto_gamer": {
        "color": "#FFFFFF",
        "modo": "apagado",
        "luces": False,
        "ultimo_comando": None
    },
    "last_update": None
}

# Simulación de sensores en segundo plano
def sensor_simulation():
    while True:
        now = datetime.now()
        
        # Actualizar humedad (40-80%)
        new_humidity = random.randint(40, 80)
        domotic_state["humedad"]["valor"] = new_humidity
        domotic_state["humedad"]["historico"].append({
            "valor": new_humidity,
            "timestamp": now.strftime("%H:%M:%S")
        })
        
        # Controlar servo motor (activa con humedad > 65%)
        if new_humidity > 65 and not domotic_state["humedad"]["estado_servo"]:
            domotic_state["humedad"]["estado_servo"] = True
        elif new_humidity <= 65 and domotic_state["humedad"]["estado_servo"]:
            domotic_state["humedad"]["estado_servo"] = False
        
        # Actualizar temperatura (20-35°C)
        new_temp = random.randint(20, 35)
        domotic_state["temperatura"]["valor"] = new_temp
        domotic_state["temperatura"]["historico"].append({
            "valor": new_temp,
            "timestamp": now.strftime("%H:%M:%S")
        })
        
        # Activar alarma si temperatura > 30°C
        domotic_state["temperatura"]["alerta"] = new_temp > 30
        
        # Mantener solo los últimos 10 registros históricos
        for sensor in ["humedad", "temperatura"]:
            if len(domotic_state[sensor]["historico"]) > 10:
                domotic_state[sensor]["historico"] = domotic_state[sensor]["historico"][-10:]
        
        domotic_state["last_update"] = now.strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(5)

# Iniciar hilo de simulación
sensor_thread = threading.Thread(target=sensor_simulation)
sensor_thread.daemon = True
sensor_thread.start()

# Rutas de la aplicación
@app.route("/")
def login():
    if "user" in session and session["user"] != "desconocido":
        return redirect(url_for("dashboard"))
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
    if "user" not in session or session["user"] == "desconocido":
        return redirect(url_for("login"))
    
    name = session["user"]
    return render_template("dashboard.html", 
                         name=name,
                         domotic_state=domotic_state)

@app.route("/control/luces", methods=["POST"])
def control_luces():
    if "user" not in session or session["user"] == "desconocido":
        return jsonify({"success": False, "error": "No autorizado"})
    
    data = request.get_json()
    color = data.get("color", "#FFFFFF")
    modo = data.get("modo", "solido")
    
    domotic_state["cuarto_gamer"]["color"] = color
    domotic_state["cuarto_gamer"]["modo"] = modo
    domotic_state["cuarto_gamer"]["luces"] = True
    domotic_state["cuarto_gamer"]["ultimo_comando"] = {
        "usuario": session["user"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accion": f"Cambio a color {color} en modo {modo}"
    }
    
    return jsonify({"success": True})

@app.route("/get_sensor_data")
def get_sensor_data():
    if "user" not in session or session["user"] == "desconocido":
        return jsonify({"success": False, "error": "No autorizado"})
    
    return jsonify({
        "success": True,
        "data": domotic_state,
        "last_update": domotic_state["last_update"]
    })

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')