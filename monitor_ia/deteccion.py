from tensorflow.keras.preprocessing.image import img_to_array
import imutils
import cv2
from tensorflow.keras.models import load_model
import numpy as np

# --- Inicialización de Modelos y Parámetros ---

eye_cascade = cv2.CascadeClassifier('haarcascade_files/haarcascade_eye.xml')

distract_model = load_model('cnn/distraction_model_tarea.hdf5', compile=False)

DNN_MODEL_PATH = './dnn_models/res10_300x300_ssd_iter_140000.caffemodel'
DNN_CONFIG_PATH = './dnn_models/deploy.prototxt.txt' 
face_detector_dnn = cv2.dnn.readNetFromCaffe(DNN_CONFIG_PATH, DNN_MODEL_PATH)

# Parámetros del frame
frame_w = 640 
border_w = 2
min_size_w = 240
min_size_h = 240
min_size_w_eye = 60
min_size_h_eye = 60
scale_factor = 1.1
min_neighbours = 5

# Video writer (COMENTAR O ELIMINAR ESTAS LÍNEAS)
# fourcc = cv2.VideoWriter_fourcc(*"MJPG")
# video_out = cv2.VideoWriter('video_out.avi', fourcc, 10.0,(640, 480))

# Inicialización de la ventana de la cámara
cv2.namedWindow('Watcha Looking At?')
camera = cv2.VideoCapture(0)

# Establecer la resolución de la cámara a 480p
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not camera.isOpened():
    print("ERROR: No se pudo abrir la cámara. ¿Está conectada y no siendo usada por otra aplicación?")
    exit()

print("Cámara abierta exitosamente. Iniciando flujo de video...")

while True:
    ret, frame = camera.read()

    if ret:
        frame = imutils.resize(frame, width=frame_w)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0))

        face_detector_dnn.setInput(blob)
        detections = face_detector_dnn.forward()

        faces_detected_dnn = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)
                faces_detected_dnn.append((startX, startY, endX - startX, endY - startY))

        if len(faces_detected_dnn) > 0:
            for (x, y, w, h) in faces_detected_dnn:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                if roi_gray.shape[0] == 0 or roi_gray.shape[1] == 0:
                    label = "Error: ROI vacio"
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0, 0, 255), 3, cv2.LINE_AA)
                    continue

                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=scale_factor, minNeighbors=min_neighbours, minSize=(min_size_w_eye, min_size_h_eye))
                
                probs = []

                if len(eyes) == 0:
                    label = 'distracted (no eyes)'
                else:
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), border_w)
                        
                        eye_roi = roi_color[ey+border_w:ey+eh-border_w, ex+border_w:ex+ew-border_w]
                        
                        if eye_roi.shape[0] > 0 and eye_roi.shape[1] > 0:
                            eye_roi = cv2.resize(eye_roi, (64, 64))
                            eye_roi = eye_roi.astype("float") / 255.0
                            eye_roi = img_to_array(eye_roi)
                            eye_roi = np.expand_dims(eye_roi, axis=0)

                            prediction = distract_model.predict(eye_roi, verbose=0)
                            
                            # print(f"Predicción del ojo: {prediction[0][0]}") 
                            probs.append(prediction[0][0]) 

                        else:
                            pass

                    if len(probs) > 0:
                        probs_mean = np.mean(probs)
                        
                        UMBRAL_ENFOQUE_OJOS = 0.4925 

                        if probs_mean >= UMBRAL_ENFOQUE_OJOS: 
                            label = 'focused'
                        else: 
                            label = 'distracted (eyes)'
                            
                    else:
                        label = 'distracted (eyes not processed)'
                
                cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 0, 255), 3, cv2.LINE_AA)
        else:
            label = "distracted (no face)"
            cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 255), 3, cv2.LINE_AA)

        # Write the frame to video (COMENTAR O ELIMINAR ESTA LÍNEA)
        # video_out.write(frame) 
        cv2.imshow('Watcha Looking At?', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("'q' presionado. Saliendo.")
            break

    else:
        print("ERROR: Fallo al leer un frame de la cámara. Saliendo del bucle.")
        break

print("Saliendo del bucle principal. Liberando cámara y destruyendo ventanas.")
camera.release()
# video_out.release() # COMENTAR O ELIMINAR ESTA LÍNEA
cv2.destroyAllWindows()