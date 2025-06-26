import cv2
import imutils
import numpy as np
import dlib
from scipy.spatial import distance as dist
import os
import base64
import json
import time
import math 

# --- Rutas de Modelos y Configuración ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo de configuración de calibración
CALIBRATION_FILE = os.path.join(BASE_DIR, 'calibration_config.json')

# Valores predeterminados para los rangos de los ojos (si no hay archivo de calibración o falla la lectura)
DEFAULT_RIGHT_EYE_RANGE_X_MIN = 200
DEFAULT_RIGHT_EYE_RANGE_X_MAX = 400
DEFAULT_RIGHT_EYE_RANGE_Y_MIN = 150
DEFAULT_RIGHT_EYE_RANGE_Y_MAX = 350

DEFAULT_LEFT_EYE_RANGE_X_MIN = 200
DEFAULT_LEFT_EYE_RANGE_X_MAX = 400
DEFAULT_LEFT_EYE_RANGE_Y_MIN = 150
DEFAULT_LEFT_EYE_RANGE_Y_MAX = 350

# --- Umbral para la detección de perfil (AJUSTA ESTE VALOR) ---
# Este valor representa el ángulo máximo (en grados) en que la cabeza puede girar
# antes de ser considerada de perfil.
# Un buen punto de partida es entre 25 y 35 grados.
# Para ajustar este valor, observa los prints de "Yaw" en tu consola mientras pruebas.
YAW_THRESHOLD_DEGREES = 30 

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
DNN_CONFIG_PATH = os.path.join(BASE_DIR, 'dnn_models', 'deploy.prototxt.txt') 
try:
    face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)
    dnn_detector_loaded = True
    print("Detector de rostros DNN de OpenCV cargado exitosamente.")
except Exception as e:
    print(f"ERROR: No se pudo cargar el detector de rostros DNN de OpenCV: {e}")
    print("Asegúrate de que los archivos .caffemodel y .prototxt.txt estén en la carpeta dnn_models/.")
    dnn_detector_loaded = False


# Predictor de 68 puntos faciales de Dlib
# Este modelo es INDISPENSABLE para la detección de distracción por perfil,
# ya que proporciona los puntos faciales (landmarks) necesarios para estimar
# la pose 3D de la cabeza (es decir, el ángulo de giro 'Yaw').
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
frame_w = 640 # Ancho de la imagen procesada para consistencia

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

# --- Definición de Puntos 3D del Modelo Facial Genérico (para estimación de pose) ---
# Estos puntos corresponden a landmarks específicos de Dlib para la estimación de pose.
# Orden: Nariz, Ojos (Izquierdo/Derecho), Boca (Izquierda/Derecha), Mentón
model_points = np.array([
    (0.0, 0.0, 0.0),             # Punto 30 (punta de la nariz)
    (-225.0, 170.0, -135.0),     # Punto 36 (canto externo del ojo izquierdo)
    (225.0, 170.0, -135.0),      # Punto 45 (canto externo del ojo derecho)
    (-150.0, -150.0, -125.0),    # Punto 48 (comisura izquierda de la boca)
    (150.0, -150.0, -125.0),     # Punto 54 (comisura derecha de la boca)
    (0.0, -330.0, -65.0)         # Punto 8 (mentón)
], dtype="double")


# --- Función para estimar la pose de la cabeza ---
def get_head_pose(shape, frame_width, frame_height, focal_length=1 * 640, center=(640 / 2, 480 / 2)):
    """
    Estima la pose de la cabeza (pitch, yaw, roll) usando los landmarks faciales 2D
    y un modelo 3D de rostro.
    """
    # Puntos 2D correspondientes a los `model_points` en el frame, extraídos de los landmarks de Dlib
    image_points = np.array([
        (shape.part(30).x, shape.part(30).y),   # Nariz
        (shape.part(36).x, shape.part(36).y),   # Ojo izquierdo externo
        (shape.part(45).x, shape.part(45).y),   # Ojo derecho externo
        (shape.part(48).x, shape.part(48).y),   # Boca izquierda
        (shape.part(54).x, shape.part(54).y),   # Boca derecha
        (shape.part(8).x, shape.part(8).y)      # Mentón
    ], dtype="double")

    # Matriz intrínseca de la cámara. Se asume que el centro óptico está en el centro de la imagen.
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    # Coeficientes de distorsión (se asume que no hay distorsión significativa de la lente)
    dist_coeffs = np.zeros((4, 1))

    # Resuelve el problema PnP (Perspective-n-Point)
    (success, rotation_vector, translation_vector) = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )

    # Convierte el vector de rotación a una matriz de rotación
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

    # Extrae los ángulos de Euler (pitch, yaw, roll) de la matriz de rotación
    # Pitch: Rotación alrededor del eje X (cabeza arriba/abajo)
    # Yaw: Rotación alrededor del eje Y (cabeza izquierda/derecha)
    # Roll: Rotación alrededor del eje Z (inclinación de la cabeza)
    sy = np.sqrt(rotation_matrix[0,0] * rotation_matrix[0,0] + rotation_matrix[1,0] * rotation_matrix[1,0])
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(rotation_matrix[2,1], rotation_matrix[2,2]) # Pitch
        y = math.atan2(-rotation_matrix[2,0], sy)                   # Yaw
        z = math.atan2(rotation_matrix[1,0], rotation_matrix[0,0]) # Roll
    else:
        x = math.atan2(-rotation_matrix[1,2], rotation_matrix[1,1])
        y = math.atan2(-rotation_matrix[2,0], sy)
        z = 0

    pitch = math.degrees(x)
    yaw = math.degrees(y)
    roll = math.degrees(z)

    return rotation_vector, translation_vector, (pitch, yaw, roll)


# --- Función principal de análisis de imagen para el backend ---
def analyze_image_for_distraction(frame):
    """
    Analiza un frame de imagen (array de NumPy/frame de OpenCV)
    y clasifica el estado de múltiples personas (atentos, distraídos, somnolientos, de perfil).
    Si no se detecta ningún rostro, se clasifica como distracción.
    La detección de "perfil" tiene prioridad sobre la detección ocular y la somnolencia.
    Retorna un diccionario con los porcentajes de cada categoría y el estado textual general.
    """
    if frame is None:
        # Si el frame es nulo, se asume distracción por falta de input.
        return {"atentos": 0, "distraidos": 100, "somnolientos": 0, "perfil": 0, "status": "Frame nulo - Distracción"}

    frame_resized = imutils.resize(frame, width=frame_w)
    (h, w) = frame_resized.shape[:2]
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    count_atentos = 0
    count_distraidos = 0
    count_somnolientos = 0
    count_perfil = 0
    total_faces_detected = 0 

    general_status = "No se detectaron rostros" # Estado general inicial

    if dnn_detector_loaded and dlib_landmark_predictor_loaded:
        blob = cv2.dnn.blobFromImage(cv2.resize(frame_resized, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        face_detector_dnn.setInput(blob)
        detections = face_detector_dnn.forward()

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2] 
            if confidence > 0.6:
                total_faces_detected += 1
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)

                if endX <= startX or endY <= startY:
                    continue

                dlib_rect_face = dlib.rectangle(startX, startY, endX, endY)

                try:
                    landmarks = landmark_predictor(gray, dlib_rect_face)
                    _, _, (pitch, yaw, roll) = get_head_pose(landmarks, w, h, focal_length=1.0 * w, center=(w / 2, h / 2))
                    
                    print(f"Rostro {total_faces_detected}: Yaw = {yaw:.2f} grados") 

                    # --- Lógica de Detección de Distracción con Prioridad ---
                    # 1. Detección de Perfil: Si la cabeza está de perfil, es distracción, sin importar los ojos.
                    if abs(yaw) > YAW_THRESHOLD_DEGREES:
                        count_perfil += 1
                        continue # Pasa al siguiente rostro, ya clasificó este como perfil
                    
                    # 2. Si NO está de perfil, verifica Somnolencia
                    right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                    left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

                    right_ear = eye_aspect_ratio(right_eye_points)
                    left_ear = eye_aspect_ratio(left_eye_points)

                    is_right_eye_closed = right_ear < EYE_CLOSED_THRESHOLD
                    is_left_eye_closed = left_ear < EYE_CLOSED_THRESHOLD

                    if is_right_eye_closed or is_left_eye_closed:
                        count_somnolientos += 1
                        continue # Pasa al siguiente rostro, ya clasificó este como somnolencia
                    
                    # 3. Si NO está de perfil y NO hay somnolencia, verifica Distracción Ocular
                    r_eye_center = eye_center(right_eye_points)
                    l_eye_center = eye_center(left_eye_points)

                    is_right_eye_in_range = (r_eye_center[0] >= RIGHT_EYE_RANGE_X_MIN and
                                             r_eye_center[0] <= RIGHT_EYE_RANGE_X_MAX and
                                             r_eye_center[1] >= RIGHT_EYE_RANGE_Y_MIN and
                                             r_eye_center[1] <= RIGHT_EYE_RANGE_Y_MAX)

                    is_left_eye_in_range = (l_eye_center[0] >= LEFT_EYE_RANGE_X_MIN and
                                            l_eye_center[0] <= LEFT_EYE_RANGE_X_MAX and
                                            l_eye_center[1] >= LEFT_EYE_RANGE_Y_MIN and
                                            l_eye_center[1] <= LEFT_EYE_RANGE_Y_MAX)

                    if is_right_eye_in_range and is_left_eye_in_range:
                        count_atentos += 1
                    else:
                        count_distraidos += 1
                
                except Exception as e:
                    # Si hay un error al procesar landmarks o pose (ej. Dlib no encuentra todos los puntos),
                    # se asume distracción por problemas en el seguimiento, pero esto es menos común si
                    # el rostro fue detectado inicialmente por DNN.
                    print(f"Error procesando landmarks o pose para un rostro: {e}")
                    count_distraidos += 1
                    continue
    
    # Calcular porcentajes generales y determinar el estado final
    atentos_percent = 0
    distraidos_percent = 0
    somnolientos_percent = 0
    perfil_percent = 0

    if total_faces_detected > 0:
        atentos_percent = (count_atentos / total_faces_detected) * 100
        distraidos_percent = (count_distraidos / total_faces_detected) * 100
        somnolientos_percent = (count_somnolientos / total_faces_detected) * 100
        perfil_percent = (count_perfil / total_faces_detected) * 100
        
        # Determinar el estado general predominante con prioridades
        if perfil_percent > 0: # Mayor prioridad: distracción por perfil
            general_status = "Distracción (Perfil)"
        elif somnolientos_percent > 0: # Siguiente prioridad: somnolencia
            general_status = "Somnolencia Detectada"
        elif distraidos_percent > 0 and (distraidos_percent >= atentos_percent): # Luego: distracción ocular
            general_status = "Distracción Predominante"
        else: # Finalmente: atención
            general_status = "Atención Predominante"
    else:
        # Si no se detecta ningún rostro, se clasifica como distracción total
        general_status = "Distracción (No hay rostro)"
        distraidos_percent = 100 # 100% de distracción
        atentos_percent = 0
        somnolientos_percent = 0
        perfil_percent = 0


    return {
        "atentos": round(atentos_percent, 2),
        "distraidos": round(distraidos_percent, 2),
        "somnolientos": round(somnolientos_percent, 2),
        "perfil": round(perfil_percent, 2),
        "status": general_status,
        "total_rostros": total_faces_detected
    }

# --- Configuración de la Cámara y Bucle de Procesamiento ---
CAP_SOURCE = 0 
FRAME_WIDTH = 640

# Queremos procesar un frame cada 0.7 segundos
PROCESS_INTERVAL = 0.7 # segundos

def run_distraction_analysis_loop():
    cap = cv2.VideoCapture(CAP_SOURCE)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la fuente de video {CAP_SOURCE}")
        print("Asegúrate de que la cámara esté conectada y no esté en uso por otra aplicación.")
        print("Si usas una cámara externa, puede que necesites un índice diferente a 0 (ej. 1, 2).")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)

    last_process_time = time.time()

    print(f"\n--- Iniciando el bucle de análisis de distracción ---")
    print(f"Procesando frames cada {PROCESS_INTERVAL} segundos.")
    print("Observa los valores de 'Yaw' en la consola para ajustar YAW_THRESHOLD_DEGREES.")
    print("Si no se detecta tu rostro o este está de perfil, se reportará como distracción.")
    print("Presiona 'q' si aparece una ventana de video, o Ctrl+C para detener el proceso.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame. Posiblemente el stream ha terminado o la cámara se desconectó. Saliendo...")
            break

        current_time = time.time()
        
        if (current_time - last_process_time) >= PROCESS_INTERVAL:
            print(f"\n--- Procesando frame a los {current_time:.2f} segundos ---")
            
            results = analyze_image_for_distraction(frame)
            
            print("Resultados de la detección:")
            print(json.dumps(results, indent=4))

            last_process_time = current_time

        # Opcional: Muestra el frame de la cámara (descomenta para depuración visual)
        # cv2.imshow("Stream de Camara (Solo para depuracion)", frame) 
        
        # Opcional: Permite salir presionando 'q' (si cv2.imshow está activo)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    run_distraction_analysis_loop()