import os
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import imutils

# Cargar modelos de OpenCV y Keras con manejo de errores
try:
    face_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise IOError("No se pudo cargar haarcascade_frontalface_default.xml")
except Exception as e:
    print(f"Error cargando face_cascade: {e}")
    face_cascade = None

try:
    eye_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_eye.xml')
    if eye_cascade.empty():
        raise IOError("No se pudo cargar haarcascade_eye.xml")
except Exception as e:
    print(f"Error cargando eye_cascade: {e}")
    eye_cascade = None

try:
    distract_model_b = load_model('./cnn/distraction_model.hdf5', compile=False)
except Exception as e:
    print(f"Error cargando distract_model_b: {e}")
    distract_model_b = None

try:
    import dlib
    shape_predictor = dlib.shape_predictor('./cnn/shape_predictor_68_face_landmarks.dat')
except Exception as e:
    print(f"Error cargando shape_predictor: {e}")
    shape_predictor = None

# Parámetros de la cámara y el procesamiento de la imagen
frame_w = 1200
border_w = 2
min_size_w = 240
min_size_h = 240
min_size_w_eye = 60
min_size_h_eye = 60
scale_factor = 1.1
min_neighbours = 5

# --- Elimina la ejecución automática del bucle de cámara ---
# --- Encapsula la lógica en una función para pruebas locales ---

def ejecutar_camara():
    cv2.namedWindow('Watcha Looking At?')
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Unable to read camera feed")
        return

    while True:
        ret, frame = camera.read()

        if ret:
            frame = imutils.resize(frame, width=frame_w)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if face_cascade is not None:
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=scale_factor, minNeighbors=min_neighbours,
                    minSize=(min_size_w, min_size_h), flags=cv2.CASCADE_SCALE_IMAGE
                )
            else:
                faces = []

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]

                if eye_cascade is not None:
                    eyes = eye_cascade.detectMultiScale(
                        roi_gray, scaleFactor=scale_factor, minNeighbors=min_neighbours,
                        minSize=(min_size_w_eye, min_size_h_eye)
                    )
                else:
                    eyes = []

                if len(eyes) > 0 and distract_model_b is not None:
                    probs = []

                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), border_w)
                        roi = roi_color[ey + border_w:ey + eh - border_w, ex + border_w:ex + ew - border_w]
                        roi = cv2.resize(roi, (64, 64))
                        roi = roi.astype("float") / 255.0
                        roi = img_to_array(roi)
                        roi = np.expand_dims(roi, axis=0)
                        prediction_b = distract_model_b.predict(roi)
                        probs.append(prediction_b[0])

                    probs_mean = np.mean(probs)
                    if probs_mean <= 0.5:
                        label = 'Distracted'
                    else:
                        label = 'Focused'

                    if len(eyes) == 1 and label == 'Distracted':
                        label = 'Distracted (profile view)'

                    # Aquí podrías usar shape_predictor para obtener landmarks si lo necesitas,
                    # pero NO para predecir distracción como un modelo Keras.
                    # Ejemplo de uso correcto (opcional, solo si tienes landmarks):
                    # if label == 'Distracted' and shape_predictor is not None:
                    #     rect = dlib.rectangle(x, y, x + w, y + h)
                    #     landmarks = shape_predictor(gray, rect)
                    #     # Aquí podrías analizar los landmarks si lo necesitas

                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)

            cv2.imshow('Watcha Looking At?', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    camera.release()
    cv2.destroyAllWindows()

# --- Fin de la función ---

# No ejecutes nada automáticamente al importar este módulo.
# Así, Django podrá importar este archivo sin abrir la cámara ni bloquear
def analizar_imagen(frame):
    """
    Stub temporal para evitar errores de importación en Django.
    Retorna resultados simulados para que el frontend pueda seguir funcionando.
    """
    # Aquí puedes poner lógica real cuando tengas los modelos y archivos necesarios.
    # Por ahora, devolvemos valores de ejemplo.
    return {
        "atentos": 60,
        "distraidos": 30,
        "somnolientos": 10
    }
