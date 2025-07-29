from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import face_recognition
import cv2
import numpy as np
import base64
import os
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "clave_super_secreta"
CORS(app)

# Estado del sistema (simulación)
system_state = {
    "humedad": {
        "valor": 45,
        "estado_servo": False,
        "history": []
    },
    "temperatura": {
        "valor": 25,
        "alerta": False,
        "history": []
    },
    "cuarto_gamer": {
        "color": "#FFFFFF",
        "modo": "solido",
        "ultimo_comando": None,
        "rgb": {
            "rojo": False,
            "verde": False,
            "azul": False
        }
    },
    "proximidad": {
        "detectado": False,
        "led_estado": False
    }
}

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

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Endpoints para el ESP32
@app.route("/api/update_sensors", methods=["POST"])
def update_sensors():
    data = request.get_json()
    
    # Actualizar humedad y controlar servo
    if "humedad" in data:
        humedad = float(data["humedad"])
        system_state["humedad"]["valor"] = humedad
        system_state["humedad"]["history"].append({"valor": humedad, "timestamp": datetime.now().isoformat()})
        
        # Control del servo (umbral 65%)
        if humedad > 65 and not system_state["humedad"]["estado_servo"]:
            system_state["humedad"]["estado_servo"] = True
        elif humedad <= 65 and system_state["humedad"]["estado_servo"]:
            system_state["humedad"]["estado_servo"] = False
    
    # Actualizar temperatura y controlar buzzer
    if "temperatura" in data:
        temperatura = float(data["temperatura"])
        system_state["temperatura"]["valor"] = temperatura
        system_state["temperatura"]["history"].append({"valor": temperatura, "timestamp": datetime.now().isoformat()})
        
        # Control de alarma (umbral 30°C)
        system_state["temperatura"]["alerta"] = temperatura > 30
    
    # Actualizar sensor de proximidad
    if "proximidad" in data:
        system_state["proximidad"]["detectado"] = bool(data["proximidad"])
        if system_state["proximidad"]["detectado"]:
            system_state["proximidad"]["led_estado"] = True
        else:
            system_state["proximidad"]["led_estado"] = False
    
    return jsonify({"success": True})

@app.route("/api/get_commands")
def get_commands():
    commands = {
        "servo": system_state["humedad"]["estado_servo"],
        "buzzer": system_state["temperatura"]["alerta"],
        "rgb": system_state["cuarto_gamer"]["rgb"],
        "proximidad_led": system_state["proximidad"]["led_estado"]
    }
    return jsonify(commands)

# Endpoints para el dashboard
@app.route("/get_sensor_data")
def get_sensor_data():
    return jsonify({
        "success": True,
        "data": system_state,
        "last_update": datetime.now().strftime("%H:%M:%S")
    })

@app.route("/control/luces", methods=["POST"])
def control_luces():
    data = request.get_json()
    color = data.get("color", "#FFFFFF")
    modo = data.get("modo", "solido")
    
    # Convertir color HEX a RGB
    color_hex = color.lstrip('#')
    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Actualizar estado
    system_state["cuarto_gamer"]["color"] = color
    system_state["cuarto_gamer"]["modo"] = modo
    system_state["cuarto_gamer"]["rgb"] = {
        "rojo": rgb[0] > 127,
        "verde": rgb[1] > 127,
        "azul": rgb[2] > 127
    }
    system_state["cuarto_gamer"]["ultimo_comando"] = {
        "accion": f"Cambio de luces a {color} en modo {modo}",
        "usuario": session.get("user", "desconocido"),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")