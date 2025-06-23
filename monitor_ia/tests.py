# C:\Users\elliot alderson\Desktop\Nueva carpeta (2)\Proyecto_Final_Construccion1\monitor_ia\test_local_detection.py

import cv2
import imutils
import numpy as np
import dlib # Aunque no se usa directamente en este archivo, se necesita para la lógica interna de deteccion.py
from scipy.spatial import distance as dist # Igual que dlib, se necesita para la lógica interna
import os # Necesario para la función que importamos

# Importa la función principal de análisis y los parámetros/funciones auxiliares desde tu módulo de detección
from .deteccion import analyze_image_for_distraction, eye_center, eye_aspect_ratio, \
                       EYE_CLOSED_THRESHOLD, \
                       CENTER_RIGHT_EYE_X_MIN, CENTER_RIGHT_EYE_X_MAX, \
                       CENTER_RIGHT_EYE_Y_MIN, CENTER_RIGHT_EYE_Y_MAX, \
                       CENTER_LEFT_EYE_X_MIN, CENTER_LEFT_EYE_X_MAX, \
                       CENTER_LEFT_EYE_Y_MIN, CENTER_LEFT_EYE_Y_MAX, \
                       EYE_POS_TOLERANCE_X, EYE_POS_TOLERANCE_Y, \
                       face_detector_dnn, dnn_detector_loaded, \
                       landmark_predictor, dlib_landmark_predictor_loaded

# Parámetros de la ventana de visualización (pueden ser diferentes del frame_w de procesamiento)
DISPLAY_FRAME_WIDTH = 640

if __name__ == "__main__":
    print("Ejecutando script de prueba local de IA (requiere cámara).")
    cv2.namedWindow('Deteccion de Distraccion Ocular (Modo Local)')
    camera = cv2.VideoCapture(0) # Tu camara PS3 Eye, ajusta el indice si no es 0

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara. ¿Está conectada y no siendo usada por otra aplicación?")
        print("Intenta cambiar el índice de la cámara en 'cv2.VideoCapture(0)' a 1, 2, etc.")
        exit()

    print("Cámara abierta exitosamente. Iniciando flujo de video local...")

    # Bucle Principal de Procesamiento de Frames
    while True:
        ret, frame = camera.read()

        if ret:
            if frame is None:
                print("ADVERTENCIA: Frame capturado es nulo. Posible problema de cámara.")
                break
            
            # Llamar a la función de análisis. Le pasamos el frame de OpenCV directamente.
            # analyze_image_for_distraction ahora puede recibir un frame de OpenCV o Base64.
            results = analyze_image_for_distraction(frame.copy()) # Pasa una copia para evitar modificaciones inesperadas

            # --- Visualización para el modo de prueba local ---
            # Re-procesamos para obtener los puntos y dibujarlos en el frame
            frame_display = imutils.resize(frame, width=DISPLAY_FRAME_WIDTH)
            (h, w) = frame_display.shape[:2]
            gray_display = cv2.cvtColor(frame_display, cv2.COLOR_BGR2GRAY)

            # Detección y dibujo de la cara para visualización
            face_box_dnn = None
            if dnn_detector_loaded:
                blob = cv2.dnn.blobFromImage(cv2.resize(frame_display, (300, 300)), 1.0,
                    (300, 300), (104.0, 177.0, 123.0))
                face_detector_dnn.setInput(blob)
                detections = face_detector_dnn.forward()
                for i in range(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.6:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        startX = max(0, startX); startY = max(0, startY)
                        endX = min(w, endX); endY = min(h, endY)
                        if endX > startX and endY > startY:
                            cv2.rectangle(frame_display, (startX, startY), (endX, endY), (255, 0, 0), 2)
                            face_box_dnn = (startX, startY, endX, endY)
                            break
            
            if face_box_dnn and dlib_landmark_predictor_loaded:
                dlib_rect_face = dlib.rectangle(face_box_dnn[0], face_box_dnn[1], face_box_dnn[2], face_box_dnn[3])
                landmarks = landmark_predictor(gray_display, dlib_rect_face)
                right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
                for (x, y) in np.concatenate((right_eye_points, left_eye_points)):
                    cv2.circle(frame_display, (x, y), 1, (0, 255, 255), -1)
                r_eye_center = eye_center(right_eye_points)
                l_eye_center = eye_center(left_eye_points)
                cv2.circle(frame_display, r_eye_center, 3, (0, 0, 255), -1)
                cv2.circle(frame_display, l_eye_center, 3, (0, 0, 255), -1)
                
                # Mostrar la información del EAR y Posición de Ojos para depuración local
                right_ear = eye_aspect_ratio(right_eye_points)
                left_ear = eye_aspect_ratio(left_eye_points)
                ear_info = f"R_EAR: {right_ear:.2f}, L_EAR: {left_ear:.2f}"
                eye_pos_info_display = (f"R Eye Pos: ({r_eye_center[0]}, {r_eye_center[1]}) "
                                        f"L Eye Pos: ({l_eye_center[0]}, {l_eye_center[1]})")
                cv2.putText(frame_display, ear_info, (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame_display, eye_pos_info_display, (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Mostrar el estado actual obtenido de la función de análisis
            cv2.putText(frame_display, results["status"], (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Deteccion de Distraccion Ocular (Modo Local)', frame_display)

            # Si se presiona 'q', salir del bucle
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' presionado. Saliendo.")
                break
        else: # Si hubo un error al leer el frame de la cámara
            print("ERROR: Fallo al leer un frame de la cámara. Saliendo del bucle.")
            break

    # Liberar recursos al finalizar
    print("Saliendo del bucle principal. Liberando cámara y destruyendo ventanas.")
    camera.release()
    cv2.destroyAllWindows()
# Create your tests here.
