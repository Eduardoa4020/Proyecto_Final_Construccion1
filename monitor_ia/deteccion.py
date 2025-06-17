import os
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import imutils

# Cargar modelos de OpenCV y Keras
face_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_eye.xml')
distract_model_b = load_model('./cnn/distraction_model.hdf5', compile=False)
distract_model_a = load_model('./cnn/shape_predictor_68_face_landmarks.dat', compile=False)  # Modelo A

# Parámetros de la cámara y el procesamiento de la imagen
frame_w = 1200
border_w = 2
min_size_w = 240
min_size_h = 240
min_size_w_eye = 60
min_size_h_eye = 60
scale_factor = 1.1
min_neighbours = 5

# Inicializar la cámara y la ventana
cv2.namedWindow('Watcha Looking At?')
camera = cv2.VideoCapture(0)

# Verificar si la cámara está abierta correctamente
if not camera.isOpened():
    print("Unable to read camera feed")

while True:
    ret, frame = camera.read()

    if ret:
        # Redimensionar el cuadro para mejorar el rendimiento
        frame = imutils.resize(frame, width=frame_w)

        # Convertir la imagen a escala de grises para procesamiento rápido
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar la cara
        faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbours,
                                             minSize=(min_size_w, min_size_h), flags=cv2.CASCADE_SCALE_IMAGE)

        for (x, y, w, h) in faces:
            # Dibujar rectángulo alrededor de la cara
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Región de interés para los ojos
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            # Detectar ojos
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=scale_factor, minNeighbors=min_neighbours,
                                                minSize=(min_size_w_eye, min_size_h_eye))

            if len(eyes) > 0:
                probs = []

                for (ex, ey, ew, eh) in eyes:
                    # Dibujar rectángulo alrededor de los ojos
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), border_w)

                    # Seleccionar la región de interés para el ojo
                    roi = roi_color[ey + border_w:ey + eh - border_w, ex + border_w:ex + ew - border_w]
                    roi = cv2.resize(roi, (64, 64))  # Asegurarse de que tenga el tamaño correcto
                    roi = roi.astype("float") / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    # Predecir distracción con el modelo B
                    prediction_b = distract_model_b.predict(roi)
                    probs.append(prediction_b[0])

                # Promedio de las predicciones de los ojos
                probs_mean = np.mean(probs)

                # Si el promedio es bajo, la persona está distraída
                if probs_mean <= 0.5:
                    label = 'Distracted'
                else:
                    label = 'Focused'

                # Verificar si la cara está de perfil (detectando un solo ojo y la mejilla)
                if len(eyes) == 1 and label == 'Distracted':  # Solo un ojo visible
                    label = 'Distracted (profile view)'

                # Aquí añadimos la lógica para usar el modelo A si detectamos que la persona está distraída
                if label == 'Distracted':
                    # Usar el modelo A para detección de distracción general
                    frame_resized = cv2.resize(frame, (64, 64))  # Ajustamos el tamaño para el modelo A
                    frame_resized = frame_resized / 255.0  # Normalización
                    frame_resized = np.expand_dims(frame_resized, axis=0)

                    # Predicción con el modelo A
                    prediction_a = distract_model_a.predict(frame_resized)
                    distract_a_label = 'Distracted' if prediction_a[0][0] > 0.5 else 'Focused'

                    # Si el modelo A también detecta distracción, etiquetamos como distraído
                    if distract_a_label == 'Distracted':
                        label = 'Distracted (Model A & B)'
                    else:
                        label = 'Focused'

                # Mostrar la etiqueta en la imagen
                cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
        
        # Mostrar el cuadro con la predicción en la ventana
        cv2.imshow('Watcha Looking At?', frame)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        break

# Liberar la cámara y cerrar ventanas
camera.release()
cv2.destroyAllWindows()
