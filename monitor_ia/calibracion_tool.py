# C:\Users\elliot alderson\Desktop\Nueva carpeta (2)\Proyecto_Final_Construccion1\monitor_ia\calibration_tool.py

# C:\Users\elliot alderson\Desktop\Nueva carpeta (2)\Proyecto_Final_Construccion1\monitor_ia\calibration_tool.py

import cv2
import numpy as np
import dlib
import os
import time
import json
import imutils # Asegúrate de tener imutils instalado: pip install imutils
from scipy.spatial import distance as dist # Para calcular EAR

print("--- Herramienta de Calibración de Atención Universal ---")
print("Este script te guiará para capturar tu mirada 'atenta' y guardar la configuración.")
print("Por favor, mira a la cámara y varía ligeramente la posición de tu cabeza/ojos mientras estás atento.")
print("Asegúrate de que los modelos de IA estén en las rutas correctas.")

# --- Rutas de Modelos y Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Ruta de la carpeta monitor_ia

# Rutas a los modelos (igual que en deteccion.py)
DNN_MODEL_PATH = os.path.join(BASE_DIR, 'dnn_models', 'res10_300x300_ssd_iter_140000.caffemodel')
DNN_CONFIG_PATH = os.path.join(BASE_DIR, 'dnn_models', 'deploy.prototxt.txt')
LANDMARKS_MODEL_PATH = os.path.join(BASE_DIR, 'dlib_models', 'shape_predictor_68_face_landmarks.dat')

CALIBRATION_FILE = os.path.join(BASE_DIR, 'calibration_config.json')

# --- Cargar Detector de Rostros DNN de OpenCV ---
try:
    face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)
    dnn_detector_loaded = True
    print("Detector de rostros DNN de OpenCV cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el detector de rostros DNN de OpenCV: {e}")
    print("Asegúrate de que los archivos .caffemodel y .prototxt estén en la carpeta dnn_models/.")
    dnn_detector_loaded = False
    exit() # Si no carga el detector, no podemos continuar

# --- Cargar Predictor de 68 puntos faciales de Dlib ---
try:
    landmark_predictor = dlib.shape_predictor(LANDMARKS_MODEL_PATH)
    dlib_landmark_predictor_loaded = True
    print("Predictor de landmarks de Dlib cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el predictor de landmarks de Dlib: {e}")
    print(f"Asegúrate de que '{LANDMARKS_MODEL_PATH}' exista y el archivo .dat no esté corrupto.")
    dlib_landmark_predictor_loaded = False
    exit() # Si no carga el predictor, no podemos continuar

# Parámetros generales
frame_w = 640 # Ancho al que se redimensionan los frames para procesamiento

# --- Función: Relación de Aspecto del Ojo (EAR) ---
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# --- Función Auxiliar para extraer el centroide del ojo ---
def eye_center(eye_points):
    xs = [p[0] for p in eye_points]
    ys = [p[1] for p in eye_points]
    center_x = int(np.mean(xs))
    center_y = int(np.mean(ys))
    return (center_x, center_y)

# --- INICIO DEL SCRIPT DE CALIBRACIÓN ---

cap = cv2.VideoCapture(0) # Accede a la primera cámara (ID 0)
if not cap.isOpened():
    print("ERROR: No se pudo abrir la cámara. Asegúrate de que no esté en uso o que tienes los drivers correctos.")
    exit()

calibrated_right_eyes_x = []
calibrated_right_eyes_y = []
calibrated_left_eyes_x = []
calibrated_left_eyes_y = []

# Número de fotos recomendado
num_frames_to_capture = 220 # Puedes ajustar cuántas fotos quieres para el aprendizaje

frames_captured = 0
capture_interval = 1.5 # Segundos entre cada captura

print(f"\nPreparado para capturar {num_frames_to_capture} frames de calibración...")
print("Presiona 'q' para salir en cualquier momento.")
print("Mantén tu rostro en el centro del encuadre y mira atentamente a la cámara.")

last_capture_time = time.time()

while frames_captured < num_frames_to_capture:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer frame de la cámara. Saliendo...")
        break

    frame_copy = frame.copy()
    frame_resized = imutils.resize(frame_copy, width=frame_w)
    (h, w) = frame_resized.shape[:2]
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    face_detected_in_frame = False
    
    blob = cv2.dnn.blobFromImage(cv2.resize(frame_resized, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    face_detector_dnn.setInput(blob)
    detections = face_detector_dnn.forward()

    face_box_dnn = None
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6: # Umbral de confianza para la detección facial
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)

            if endX > startX and endY > startY:
                face_box_dnn = (startX, startY, endX, endY)
                cv2.rectangle(frame_resized, (startX, startY), (endX, endY), (0, 255, 0), 2) # Dibuja el rostro
                face_detected_in_frame = True
                break

    if face_box_dnn and (time.time() - last_capture_time) > capture_interval:
        dlib_rect_face = dlib.rectangle(face_box_dnn[0], face_box_dnn[1], face_box_dnn[2], face_box_dnn[3])
        try:
            landmarks = landmark_predictor(gray, dlib_rect_face)
            
            right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

            r_eye_center = eye_center(right_eye_points)
            l_eye_center = eye_center(left_eye_points)

            # Opcional: filtro básico para evitar valores atípicos (e.g., si parpadeas justo en la captura)
            # Podrías agregar más lógica aquí si los puntos son muy inestables.
            if eye_aspect_ratio(right_eye_points) > 0.25 and eye_aspect_ratio(left_eye_points) > 0.25:
                calibrated_right_eyes_x.append(r_eye_center[0])
                calibrated_right_eyes_y.append(r_eye_center[1])
                calibrated_left_eyes_x.append(l_eye_center[0])
                calibrated_left_eyes_y.append(l_eye_center[1])
                
                frames_captured += 1
                last_capture_time = time.time()
                print(f"Frame {frames_captured}/{num_frames_to_capture} capturado. R-Eye: {r_eye_center}, L-Eye: {l_eye_center}")

                cv2.circle(frame_resized, r_eye_center, 3, (255, 0, 0), -1)
                cv2.circle(frame_resized, l_eye_center, 3, (255, 0, 0), -1)
            else:
                print("Advertencia: Ojo cerrado detectado en la calibración. Saltando este frame.")


        except Exception as e:
            print(f"Advertencia: No se pudieron obtener landmarks para un rostro durante la calibración: {e}")
    
    cv2.putText(frame_resized, f"Capturando: {frames_captured}/{num_frames_to_capture}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if not face_detected_in_frame:
        cv2.putText(frame_resized, "No se detecta rostro. Centra tu cara.", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Calibracion - Mirada Atenta", frame_resized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Calibración cancelada por el usuario.")
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

# --- Guardar los promedios en un archivo de configuración ---
if frames_captured > 0:
    avg_right_eye_x = int(np.mean(calibrated_right_eyes_x))
    avg_right_eye_y = int(np.mean(calibrated_right_eyes_y))
    avg_left_eye_x = int(np.mean(calibrated_left_eyes_x))
    avg_left_eye_y = int(np.mean(calibrated_left_eyes_y))

    calibration_data = {
        "CALIBRATED_RIGHT_EYE_CENTER_X": avg_right_eye_x,
        "CALIBRATED_RIGHT_EYE_CENTER_Y": avg_right_eye_y,
        "CALIBRATED_LEFT_EYE_CENTER_X": avg_left_eye_x,
        "CALIBRATED_LEFT_EYE_CENTER_Y": avg_left_eye_y,
        # Puedes añadir una tolerancia predeterminada aquí o dejarla fija en deteccion.py
        "EYE_POS_TOLERANCE_X": 10, # Esta tolerancia se usará en deteccion.py
        "EYE_POS_TOLERANCE_Y": 10  # Esta tolerancia se usará en deteccion.py
    }

    try:
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(calibration_data, f, indent=4)
        print(f"\n¡Calibración exitosa! Los datos se han guardado en {CALIBRATION_FILE}")
        print("Recuerda reiniciar tu servidor Django para que los cambios surtan efecto en el monitoreo.")
    except Exception as e:
        print(f"\nERROR: No se pudo guardar el archivo de calibración: {e}")
else:
    print("No se pudieron capturar suficientes frames para la calibración. El archivo de configuración no se generó.")