import cv2
import imutils
import numpy as np
import dlib
from scipy.spatial import distance as dist
import os 
import base64 # Asegúrate de que esto esté aquí

# --- Rutas de Modelos y Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detector de rostros DNN de OpenCV
DNN_MODEL_PATH = os.path.join(BASE_DIR, 'dnn_models', 'res10_300x300_ssd_iter_140000.caffemodel')
DNN_CONFIG_PATH = os.path.join(BASE_DIR, 'dnn_models', 'deploy.prototxt.txt') # ¡IMPORTANTE! Sin .txt aquí
try:
    face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)
    dnn_detector_loaded = True
    print("Detector de rostros DNN de OpenCV cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el detector de rostros DNN de OpenCV: {e}")
    print("Asegúrate de que los archivos .caffemodel y .prototxt estén en la carpeta dnn_models/.")
    dnn_detector_loaded = False


# Predictor de 68 puntos faciales de Dlib
LANDMARKS_MODEL_PATH = os.path.join(BASE_DIR, 'dlib_models', 'shape_predictor_68_face_landmarks.dat')
try:
    landmark_predictor = dlib.shape_predictor(LANDMARKS_MODEL_PATH)
    dlib_landmark_predictor_loaded = True
    print("Predictor de landmarks de Dlib cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el predictor de landmarks de Dlib: {e}")
    print(f"Asegúrate de que '{LANDMARKS_MODEL_PATH}' exista y el archivo .dat no esté corrupto.")
    dlib_landmark_predictor_loaded = False

# Parámetros generales
frame_w = 640

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

# --- UMBRALES DE DETECCIÓN DE OJO CERRADO ---
EYE_CLOSED_THRESHOLD = 0.20 

# --- UMBRALES DE ENFOQUE OCULAR PERSONALIZADOS ---
CENTER_RIGHT_EYE_X_MIN = 250
CENTER_RIGHT_EYE_X_MAX = 280
CENTER_RIGHT_EYE_Y_MIN = 215
CENTER_RIGHT_EYE_Y_MAX = 240
CENTER_LEFT_EYE_X_MIN = 320
CENTER_LEFT_EYE_X_MAX = 355
CENTER_LEFT_EYE_Y_MIN = 220
CENTER_LEFT_EYE_Y_MAX = 235
EYE_POS_TOLERANCE_X = 5
EYE_POS_TOLERANCE_Y = 5
# --- FIN DE UMBRALES DE ENFOQUE OCULAR ---

# --- Función principal de análisis de imagen para el backend ---
def analyze_image_for_distraction(frame):
    """
    Analiza un frame de imagen (debe ser un array de NumPy/frame de OpenCV)
    y clasifica el estado del conductor.
    Retorna un diccionario con los porcentajes de cada categoría y el estado textual.
    """
    if frame is None:
        return {"atentos": 0, "distraidos": 0, "somnolientos": 0, "status": "Frame nulo"}

    # Redimensionar el frame para procesamiento
    frame_resized = imutils.resize(frame, width=frame_w)
    (h, w) = frame_resized.shape[:2]
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    # Inicializamos los estados de salida
    current_status = "No face detected"
    atentos_percent = 0
    distraidos_percent = 0
    somnolientos_percent = 0

    if dnn_detector_loaded and dlib_landmark_predictor_loaded:
        # --- Detección de Rostros con DNN de OpenCV ---
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

                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)

                if endX > startX and endY > startY:
                    face_box_dnn = (startX, startY, endX, endY)
                    break

        if face_box_dnn:
            dlib_rect_face = dlib.rectangle(face_box_dnn[0], face_box_dnn[1],
                                            face_box_dnn[2], face_box_dnn[3])

            landmarks = landmark_predictor(gray, dlib_rect_face)

            # --- Extracción y Procesamiento de Puntos Oculares ---
            right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y)
                                         for i in range(36, 42)])
            left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y)
                                        for i in range(42, 48)])

            # Calcular el EAR para cada ojo
            right_ear = eye_aspect_ratio(right_eye_points)
            left_ear = eye_aspect_ratio(left_eye_points)

            # --- Lógica de Clasificación del Estado del Conductor ---
            is_right_eye_closed = right_ear < EYE_CLOSED_THRESHOLD
            is_left_eye_closed = left_ear < EYE_CLOSED_THRESHOLD

            if is_right_eye_closed or is_left_eye_closed:
                current_status = "Somnoliento"
                somnolientos_percent = 100
                distraidos_percent = 0
                atentos_percent = 0
            else:
                r_eye_center = eye_center(right_eye_points)
                l_eye_center = eye_center(left_eye_points)

                is_right_eye_centered_x = (r_eye_center[0] >= CENTER_RIGHT_EYE_X_MIN - EYE_POS_TOLERANCE_X and
                                           r_eye_center[0] <= CENTER_RIGHT_EYE_X_MAX + EYE_POS_TOLERANCE_X)
                is_right_eye_centered_y = (r_eye_center[1] >= CENTER_RIGHT_EYE_Y_MIN - EYE_POS_TOLERANCE_Y and
                                           r_eye_center[1] <= CENTER_RIGHT_EYE_Y_MAX + EYE_POS_TOLERANCE_Y)
                is_right_eye_centered = is_right_eye_centered_x and is_right_eye_centered_y

                is_left_eye_centered_x = (l_eye_center[0] >= CENTER_LEFT_EYE_X_MIN - EYE_POS_TOLERANCE_X and
                                          l_eye_center[0] <= CENTER_LEFT_EYE_X_MAX + EYE_POS_TOLERANCE_X)
                is_left_eye_centered_y = (l_eye_center[1] >= CENTER_LEFT_EYE_Y_MIN - EYE_POS_TOLERANCE_Y and
                                          l_eye_center[1] <= CENTER_LEFT_EYE_Y_MAX + EYE_POS_TOLERANCE_Y)
                is_left_eye_centered = is_left_eye_centered_x and is_left_eye_centered_y

                if is_right_eye_centered and is_left_eye_centered:
                    current_status = "Atento"
                    atentos_percent = 100
                    distraidos_percent = 0
                    somnolientos_percent = 0
                else:
                    current_status = "Distraido"
                    distraidos_percent = 100
                    atentos_percent = 0
                    somnolientos_percent = 0
        else:
            current_status = "Distraido (No Face)"
            distraidos_percent = 100
            atentos_percent = 0
            somnolientos_percent = 0
    else:
        current_status = "Modelos no cargados"
        atentos_percent = 0
        distraidos_percent = 0
        somnolientos_percent = 0

    return {
        "atentos": atentos_percent,
        "distraidos": distraidos_percent,
        "somnolientos": somnolientos_percent,
        "status": current_status
    }