import cv2
import imutils
import numpy as np
import dlib
from scipy.spatial import distance as dist
import os
import base64
import json

# --- Rutas de Modelos y Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo de configuración de calibración
CALIBRATION_FILE = os.path.join(BASE_DIR, 'calibration_config.json')

# Valores predeterminados para los rangos de los ojos (si no hay archivo de calibración o falla la lectura)
# Estos son valores de un rango predeterminado que puedes ajustar si es necesario.
# Son rangos amplios para evitar errores si no hay calibración.
DEFAULT_RIGHT_EYE_RANGE_X_MIN = 200
DEFAULT_RIGHT_EYE_RANGE_X_MAX = 400
DEFAULT_RIGHT_EYE_RANGE_Y_MIN = 150
DEFAULT_RIGHT_EYE_RANGE_Y_MAX = 350

DEFAULT_LEFT_EYE_RANGE_X_MIN = 200
DEFAULT_LEFT_EYE_RANGE_X_MAX = 400
DEFAULT_LEFT_EYE_RANGE_Y_MIN = 150
DEFAULT_LEFT_EYE_RANGE_Y_MAX = 350


# Variables globales que se actualizarán con los valores del JSON si el archivo existe y es válido.
RIGHT_EYE_RANGE_X_MIN = DEFAULT_RIGHT_EYE_RANGE_X_MIN
RIGHT_EYE_RANGE_X_MAX = DEFAULT_RIGHT_EYE_RANGE_X_MAX
RIGHT_EYE_RANGE_Y_MIN = DEFAULT_RIGHT_EYE_RANGE_Y_MIN
RIGHT_EYE_RANGE_Y_MAX = DEFAULT_RIGHT_EYE_RANGE_Y_MAX

LEFT_EYE_RANGE_X_MIN = DEFAULT_LEFT_EYE_RANGE_X_MIN
LEFT_EYE_RANGE_X_MAX = DEFAULT_LEFT_EYE_RANGE_X_MAX
LEFT_EYE_RANGE_Y_MIN = DEFAULT_LEFT_EYE_RANGE_Y_MIN
LEFT_EYE_RANGE_Y_MAX = DEFAULT_LEFT_EYE_RANGE_Y_MAX

try:
    if os.path.exists(CALIBRATION_FILE):
        with open(CALIBRATION_FILE, 'r') as f:
            calibration_data = json.load(f)
        
        # Actualiza las variables globales con los valores cargados del JSON
        RIGHT_EYE_RANGE_X_MIN = calibration_data.get("RIGHT_EYE_RANGE_X_MIN", DEFAULT_RIGHT_EYE_RANGE_X_MIN)
        RIGHT_EYE_RANGE_X_MAX = calibration_data.get("RIGHT_EYE_RANGE_X_MAX", DEFAULT_RIGHT_EYE_RANGE_X_MAX)
        RIGHT_EYE_RANGE_Y_MIN = calibration_data.get("RIGHT_EYE_RANGE_Y_MIN", DEFAULT_RIGHT_EYE_RANGE_Y_MIN)
        RIGHT_EYE_RANGE_Y_MAX = calibration_data.get("RIGHT_EYE_RANGE_Y_MAX", DEFAULT_RIGHT_EYE_RANGE_Y_MAX)

        LEFT_EYE_RANGE_X_MIN = calibration_data.get("LEFT_EYE_RANGE_X_MIN", DEFAULT_LEFT_EYE_RANGE_X_MIN)
        LEFT_EYE_RANGE_X_MAX = calibration_data.get("LEFT_EYE_RANGE_X_MAX", DEFAULT_LEFT_EYE_RANGE_X_MAX)
        LEFT_EYE_RANGE_Y_MIN = calibration_data.get("LEFT_EYE_RANGE_Y_MIN", DEFAULT_LEFT_EYE_RANGE_Y_MIN)
        LEFT_EYE_RANGE_Y_MAX = calibration_data.get("LEFT_EYE_RANGE_Y_MAX", DEFAULT_LEFT_EYE_RANGE_Y_MAX)
        
        print(f"Configuración de calibración cargada desde {CALIBRATION_FILE} (modo rango).")
    else:
        print(f"Archivo de calibración {CALIBRATION_FILE} no encontrado. Usando valores de rango predeterminados.")
except Exception as e:
    print(f"ERROR al cargar el archivo de calibración: {e}. Usando valores de rango predeterminados.")


# Detector de rostros DNN de OpenCV
DNN_MODEL_PATH = os.path.join(BASE_DIR, 'dnn_models', 'res10_300x300_ssd_iter_140000.caffemodel')
DNN_CONFIG_PATH = os.path.join(BASE_DIR, 'dnn_models', 'deploy.prototxt.txt') # ¡IMPORTANTE: Asegúrate que tu archivo se llame así!
try:
    face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)
    dnn_detector_loaded = True
    print("Detector de rostros DNN de OpenCV cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el detector de rostros DNN de OpenCV: {e}")
    print("Asegúrate de que los archivos .caffemodel y .prototxt.txt estén en la carpeta dnn_models/.")
    dnn_detector_loaded = False


# Predictor de 68 puntos faciales de Dlib
LANDMARKS_MODEL_PATH = os.path.join(BASE_DIR, 'dlib_models', 'shape_predictor_68_face_landmarks.dat') # ¡IMPORTANTE: Asegúrate que tu archivo se llame así!
try:
    landmark_predictor = dlib.shape_predictor(LANDMARKS_MODEL_PATH)
    dlib_landmark_predictor_loaded = True
    print("Predictor de landmarks de Dlib cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el predictor de landmarks de Dlib: {e}")
    print(f"Asegúrate de que '{LANDMARKS_MODEL_PATH}' exista y el archivo .dat no esté corrupto.")
    dlib_landmark_predictor_loaded = False

# Parámetros generales
frame_w = 640 # Ancho de la imagen procesada para consistencia

# --- Función: Relación de Aspecto del Ojo (EAR) ---
# Calcula el Eye Aspect Ratio (EAR) para determinar si un ojo está abierto o cerrado.
# Un valor bajo (cercano a cero) indica ojo cerrado, un valor alto indica ojo abierto.
def eye_aspect_ratio(eye):
    # Calcula las distancias euclidianas entre los puntos verticales del ojo
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # Calcula la distancia euclidiana entre los puntos horizontales del ojo
    C = dist.euclidean(eye[0], eye[3])
    # La fórmula EAR
    ear = (A + B) / (2.0 * C)
    return ear

# --- Función Auxiliar para extraer el centroide del ojo ---
# Calcula el centro (centroide) de los puntos de un ojo.
def eye_center(eye_points):
    xs = [p[0] for p in eye_points]
    ys = [p[1] for p in eye_points]
    center_x = int(np.mean(xs))
    center_y = int(np.mean(ys))
    return (center_x, center_y)

# --- UMBRALES DE DETECCIÓN DE OJO CERRADO ---
# Este umbral define qué valor de EAR se considera un ojo cerrado.
# Un valor más bajo hace la detección de somnolencia más permisiva.
EYE_CLOSED_THRESHOLD = 0.20 

# --- Función principal de análisis de imagen para el backend ---
def analyze_image_for_distraction(frame):
    """
    Analiza un frame de imagen (array de NumPy/frame de OpenCV)
    y clasifica el estado de múltiples personas (atentos, distraídos, somnolientos).
    Utiliza valores de calibración cargados desde calibration_config.json (modo rango).
    Retorna un diccionario con los porcentajes de cada categoría y el estado textual general.
    """
    if frame is None:
        # Si el frame es nulo (ej. no se recibió imagen de la cámara), retorna un estado de error.
        return {"atentos": 0, "distraidos": 0, "somnolientos": 0, "status": "Frame nulo"}

    # Redimensionar el frame para un procesamiento más rápido y consistente
    frame_resized = imutils.resize(frame, width=frame_w)
    (h, w) = frame_resized.shape[:2] # Obtiene alto y ancho del frame redimensionado
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY) # Convierte a escala de grises para el procesamiento facial

    # Contadores para cada estado de atención
    count_atentos = 0
    count_distraidos = 0
    count_somnolientos = 0
    total_faces_detected = 0 # Contador total de rostros encontrados en el frame

    general_status = "No face detected" # Estado general inicial, por si no se detecta ningún rostro

    # Solo procede si ambos modelos de IA (DNN y Dlib) se cargaron correctamente al inicio.
    if dnn_detector_loaded and dlib_landmark_predictor_loaded:
        # Prepara la imagen para el detector de rostros DNN (Deep Neural Network)
        # El blob es una representación de la imagen adecuada para la red neuronal.
        blob = cv2.dnn.blobFromImage(cv2.resize(frame_resized, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        face_detector_dnn.setInput(blob) # Pasa el blob a la red
        detections = face_detector_dnn.forward() # Ejecuta la detección de rostros

        # Iterar sobre todas las detecciones de rostros en el frame
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2] # Obtiene la confianza de la detección actual
            if confidence > 0.6: # Si la confianza es suficientemente alta (ej. > 60%)
                total_faces_detected += 1
                # Calcula las coordenadas del cuadro delimitador del rostro detectado
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Asegura que las coordenadas estén dentro de los límites del frame (evita errores)
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)

                # Si el cuadro delimitador no es válido (ej. ancho o alto es cero o negativo), salta a la siguiente detección.
                if endX <= startX or endY <= startY:
                    continue

                # Convierte el cuadro de OpenCV a un objeto dlib.rectangle, necesario para el predictor de landmarks.
                dlib_rect_face = dlib.rectangle(startX, startY, endX, endY)

                try:
                    # Predice los 68 puntos faciales (landmarks) para el rostro detectado.
                    landmarks = landmark_predictor(gray, dlib_rect_face)
                except Exception as e:
                    # Si hay un error al procesar los landmarks, asume que la persona está distraída.
                    print(f"Error procesando landmarks para un rostro: {e}")
                    count_distraidos += 1
                    continue # Continúa con el siguiente rostro

                # Extrae los puntos específicos que corresponden a los ojos (según el mapeo de Dlib).
                # Ojo derecho: puntos 36 a 41
                right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                # Ojo izquierdo: puntos 42 a 47
                left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

                # Calcula la Relación de Aspecto del Ojo (EAR) para ambos ojos.
                right_ear = eye_aspect_ratio(right_eye_points)
                left_ear = eye_aspect_ratio(left_eye_points)

                # Determina si cada ojo está cerrado basándose en el umbral EAR.
                is_right_eye_closed = right_ear < EYE_CLOSED_THRESHOLD
                is_left_eye_closed = left_ear < EYE_CLOSED_THRESHOLD

                # Clasifica el estado de atención para este rostro individual
                if is_right_eye_closed or is_left_eye_closed:
                    # Si al menos un ojo está cerrado, la persona está somnolienta.
                    count_somnolientos += 1
                else:
                    # Si los ojos están abiertos, verifica la posición del centro de los ojos.
                    r_eye_center = eye_center(right_eye_points)
                    l_eye_center = eye_center(left_eye_points)

                    # --- Lógica de enfoque ocular utilizando los RANGOS de calibración cargados ---
                    # Compara si la posición actual del centro del ojo derecho cae dentro de su rango calibrado.
                    is_right_eye_in_range = (r_eye_center[0] >= RIGHT_EYE_RANGE_X_MIN and
                                             r_eye_center[0] <= RIGHT_EYE_RANGE_X_MAX and
                                             r_eye_center[1] >= RIGHT_EYE_RANGE_Y_MIN and
                                             r_eye_center[1] <= RIGHT_EYE_RANGE_Y_MAX)

                    # Compara si la posición actual del centro del ojo izquierdo cae dentro de su rango calibrado.
                    is_left_eye_in_range = (l_eye_center[0] >= LEFT_EYE_RANGE_X_MIN and
                                            l_eye_center[0] <= LEFT_EYE_RANGE_X_MAX and
                                            l_eye_center[1] >= LEFT_EYE_RANGE_Y_MIN and
                                            l_eye_center[1] <= LEFT_EYE_RANGE_Y_MAX)

                    # Si ambos ojos están dentro de su rango calibrado de "atención", se cuenta como atento.
                    if is_right_eye_in_range and is_left_eye_in_range:
                        count_atentos += 1
                    else:
                        # Si no están somnolientos y no están dentro del rango de atención, están distraídos.
                        count_distraidos += 1
    
    # Calcular porcentajes generales basados en el total de rostros detectados
    atentos_percent = 0
    distraidos_percent = 0
    somnolientos_percent = 0

    if total_faces_detected > 0:
        # Calcula los porcentajes si se detectaron rostros.
        atentos_percent = (count_atentos / total_faces_detected) * 100
        distraidos_percent = (count_distraidos / total_faces_detected) * 100
        somnolientos_percent = (count_somnolientos / total_faces_detected) * 100
        
        # Determinar el estado general predominante en la clase o grupo.
        if somnolientos_percent > 0:
            general_status = "Somnolencia Detectada" # La somnolencia tiene la mayor prioridad
        elif distraidos_percent > 0 and (distraidos_percent >= atentos_percent):
            general_status = "Distracción Predominante" # Si la distracción es significativa y mayor o igual que la atención
        else:
            general_status = "Atención Predominante" # Si no hay somnolencia y la atención es predominante
    else:
        # Si no se detecta ningún rostro, establece todos los porcentajes en cero y el estado a "No se detectaron rostros".
        general_status = "No se detectaron rostros"
        atentos_percent = 0
        distraidos_percent = 0
        somnolientos_percent = 0

    # Retorna un diccionario con los resultados, redondeados a dos decimales para una mejor presentación.
    return {
        "atentos": round(atentos_percent, 2),
        "distraidos": round(distraidos_percent, 2),
        "somnolientos": round(somnolientos_percent, 2),
        "status": general_status,
        "total_rostros": total_faces_detected # Útil para el frontend para saber cuánta gente se está viendo
    }