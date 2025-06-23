import imutils
import cv2
import numpy as np
import mediapipe as mp
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DNN_MODEL_PATH = os.path.join(BASE_DIR, 'dnn_models', 'res10_300x300_ssd_iter_140000.caffemodel')
DNN_CONFIG_PATH = os.path.join(BASE_DIR, 'dnn_models', 'deploy.prototxt.txt')

face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)

frame_w = 640

RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_IRISH = [474, 475, 476, 477]
LEFT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LEFT_EYE_IRISH = [469, 470, 471, 472]

EAR_THRESHOLD = 0.25
FOCUS_THRESHOLD = 15

LEFT_CENTER_X_RANGE = (-1.60, -1.40)
LEFT_CENTER_Y_RANGE = (1.18, 0.80)
RIGHT_CENTER_X_RANGE = (2.70, 2.30)
RIGHT_CENTER_Y_RANGE = (-0.48, -0.28)

LEFT_LEFT_X_RANGE = (-1.87, -1.73)
LEFT_LEFT_Y_RANGE = (0.87, 1.03)
RIGHT_LEFT_X_RANGE = (2.33, 2.48)
RIGHT_LEFT_Y_RANGE = (-0.28, -0.18)

LEFT_RIGHT_X_RANGE = (-1.33, -1.17)
LEFT_RIGHT_Y_RANGE = (0.77, 0.98)
RIGHT_RIGHT_X_RANGE = (2.55, 2.77)
RIGHT_RIGHT_Y_RANGE = (-0.23, -0.08)

LEFT_UP_X_RANGE = (-1.55, -1.35)
LEFT_UP_Y_RANGE = (0.33, 0.58)
RIGHT_UP_X_RANGE = (2.53, 2.75)
RIGHT_UP_Y_RANGE = (-0.17, 0.08)

LEFT_DOWN_X_RANGE = (-1.67, -1.47)
LEFT_DOWN_Y_RANGE = (1.03, 1.27)
RIGHT_DOWN_X_RANGE = (2.63, 2.78)
RIGHT_DOWN_Y_RANGE = (-0.37, -0.18)

def eye_aspect_ratio(eye_landmarks):
    A = np.linalg.norm(eye_landmarks[4] - eye_landmarks[10])
    B = np.linalg.norm(eye_landmarks[6] - eye_landmarks[12])
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[8])
    return 0 if C == 0 else (A + B) / (2.0 * C)

def get_gaze_direction_normalized(iris_center, eye_landmarks):
    x_coords = eye_landmarks[:, 0]
    y_coords = eye_landmarks[:, 1]
    min_x = np.min(x_coords)
    max_x = np.max(x_coords)
    min_y = np.min(y_coords)
    max_y = np.max(y_coords)

    eye_width = max_x - min_x
    eye_height = max_y - min_y

    normalized_x = (iris_center[0] - min_x) / eye_width if eye_width > 0 else 0.5  
    normalized_y = (iris_center[1] - min_y) / eye_height if eye_height > 0 else 0.5  

    return normalized_x, normalized_y

def is_iris_out_of_bounds(iris_x, eye_side):
    if eye_side == "left":
        return iris_x < -1.72 or iris_x > -1.39
    elif eye_side == "right":
        return iris_x < 2.44 or iris_x > 2.69
    return True

def get_face_rotation_angle(left_eye_center, right_eye_center):
    delta_y = right_eye_center[1] - left_eye_center[1]
    delta_x = right_eye_center[0] - left_eye_center[0]
    return np.arctan2(delta_y, delta_x) * 180.0 / np.pi

def analizar_video(video_path=0, mostrar_ventana=False):
    mp_face_mesh = mp.solutions.face_mesh
    distracted_frames = 0

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("ERROR: No se pudo abrir el video o la cámara.")
        return

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = imutils.resize(frame, width=frame_w)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]

            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            face_detector_dnn.setInput(blob)
            detections = face_detector_dnn.forward()
            face_detected_by_dnn = False

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.6:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
                    face_detected_by_dnn = True
                    break

            results = face_mesh.process(frame_rgb)
            text_status = "Rostro no detectado"

            if face_detected_by_dnn and results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                left_eye_points = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in LEFT_EYE_LANDMARKS])
                right_eye_points = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in RIGHT_EYE_LANDMARKS])
                left_iris_points = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in LEFT_EYE_IRISH])
                right_iris_points = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in RIGHT_EYE_IRISH])

                left_iris_center = None
                right_iris_center = None
                if len(left_iris_points) > 0:
                    left_iris_center = (int(np.mean(left_iris_points[:,0])), int(np.mean(left_iris_points[:,1])))
                if len(right_iris_points) > 0:
                    right_iris_center = (int(np.mean(right_iris_points[:,0])), int(np.mean(right_iris_points[:,1])))

                ear_left = eye_aspect_ratio(left_eye_points)
                ear_right = eye_aspect_ratio(right_eye_points)
                avg_ear = (ear_left + ear_right) / 2.0

                left_eye_center = np.mean(left_eye_points, axis=0)
                right_eye_center = np.mean(right_eye_points, axis=0)
                angle = get_face_rotation_angle(left_eye_center, right_eye_center)

                if left_iris_center is not None and len(left_eye_points) > 0 and right_iris_center is not None and len(right_eye_points) > 0:
                    normalized_x_left, normalized_y_left = get_gaze_direction_normalized(left_iris_center, left_eye_points)
                    normalized_x_right, normalized_y_right = get_gaze_direction_normalized(right_iris_center, right_eye_points)

                    looking_center = (LEFT_CENTER_X_RANGE[0] <= normalized_x_left <= LEFT_CENTER_X_RANGE[1] and
                                     LEFT_CENTER_Y_RANGE[0] <= normalized_y_left <= LEFT_CENTER_Y_RANGE[1] and
                                     RIGHT_CENTER_X_RANGE[0] <= normalized_x_right <= RIGHT_CENTER_X_RANGE[1] and
                                     RIGHT_CENTER_Y_RANGE[0] <= normalized_y_right <= RIGHT_CENTER_Y_RANGE[1])

                    looking_left = (LEFT_LEFT_X_RANGE[0] <= normalized_x_left <= LEFT_LEFT_X_RANGE[1] and
                                   LEFT_LEFT_Y_RANGE[0] <= normalized_y_left <= LEFT_LEFT_Y_RANGE[1] and
                                   RIGHT_LEFT_X_RANGE[0] <= normalized_x_right <= RIGHT_LEFT_X_RANGE[1] and
                                   RIGHT_LEFT_Y_RANGE[0] <= normalized_y_right <= RIGHT_LEFT_Y_RANGE[1])

                    looking_right = (LEFT_RIGHT_X_RANGE[0] <= normalized_x_left <= LEFT_RIGHT_X_RANGE[1] and
                                    LEFT_RIGHT_Y_RANGE[0] <= normalized_y_left <= LEFT_RIGHT_Y_RANGE[1] and
                                    RIGHT_RIGHT_X_RANGE[0] <= normalized_x_right <= RIGHT_RIGHT_X_RANGE[1] and
                                    RIGHT_RIGHT_Y_RANGE[0] <= normalized_y_right <= RIGHT_RIGHT_Y_RANGE[1])

                    looking_up = (LEFT_UP_X_RANGE[0] <= normalized_x_left <= LEFT_UP_X_RANGE[1] and
                                 LEFT_UP_Y_RANGE[0] <= normalized_y_left <= LEFT_UP_Y_RANGE[1] and
                                 RIGHT_UP_X_RANGE[0] <= normalized_x_right <= RIGHT_UP_X_RANGE[1] and
                                 RIGHT_UP_Y_RANGE[0] <= normalized_y_right <= RIGHT_UP_Y_RANGE[1])

                    looking_down = (LEFT_DOWN_X_RANGE[0] <= normalized_x_left <= LEFT_DOWN_X_RANGE[1] and
                                   LEFT_DOWN_Y_RANGE[0] <= normalized_y_left <= LEFT_DOWN_Y_RANGE[1] and
                                   RIGHT_DOWN_X_RANGE[0] <= normalized_x_right <= RIGHT_DOWN_X_RANGE[1] and
                                   RIGHT_DOWN_Y_RANGE[0] <= normalized_y_right <= RIGHT_DOWN_Y_RANGE[1])

                    if looking_center:
                        text_status = "Distraido"
                    elif looking_left:
                        text_status = "Atento"
                    elif looking_right:
                        text_status = "Atento"
                    elif looking_up:
                        text_status = "Atento"
                    elif looking_down:
                        text_status = "Atento"
                    else:
                        text_status = "Atento"
                else:
                    text_status = "No se detectan los iris"

                if "Distraido" in text_status:
                    distracted_frames += 1
                else:
                    distracted_frames = 0

                if distracted_frames >= FOCUS_THRESHOLD and mostrar_ventana:
                    cv2.putText(frame, "ALERTA: Distraccion Sostenida", (10, h - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

                color = (0, 255, 0) if "Atento" in text_status else (0, 0, 255)
                if mostrar_ventana:
                    cv2.putText(frame, text_status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

            else:
                text_status = "Rostro no detectado"

            if mostrar_ventana:
                cv2.imshow('Deteccion de Distraccion (MediaPipe)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    if mostrar_ventana:
        cv2.destroyAllWindows()

def analizar_imagen(frame):
  
    return {"status": "ok", "mensaje": "Función analizar_imagen aún no implementada"}

# No hay ejecución automática ni ejemplos activos.