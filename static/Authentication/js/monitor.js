let stream = null;
let intervaloEnvio = null;
let timerInterval = null;
let elapsedTime = 0;
let mediaRecorder = null;
let recordedChunks = [];

const video = document.getElementById('video');
const canvas = document.getElementById('snapshot');
const context = canvas.getContext('2d');
const btnIniciar = document.getElementById('start-monitoring');
const btnDetener = document.getElementById('stop-monitoring');
const btnReset = document.getElementById('reset-monitoring');
const alerta = document.getElementById('attention-alert'); // Ya definida
const timerDisplay = document.getElementById('session-timer');
const btnDescargarGrabacion = document.createElement('a');

btnDescargarGrabacion.textContent = "Descargar grabación";
btnDescargarGrabacion.className = "px-3 py-1 bg-blue-600 text-white rounded-md flex items-center mt-4";
btnDescargarGrabacion.style.display = "none";
btnDescargarGrabacion.download = "grabacion.webm";
document.querySelector('#monitoring-page').appendChild(btnDescargarGrabacion);

async function verificarCamara() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const hayCamara = devices.some(device => device.kind === 'videoinput');

    const statusSpan = document.getElementById('camera-status');
    const icon = document.getElementById('camera-icon');
    const text = document.getElementById('camera-text');

    statusSpan.classList.remove('estado-conectado', 'estado-desconectado');

    if (hayCamara) {
      statusSpan.classList.add('estado-conectado');
      text.textContent = 'Cámara conectada';
      // Mover la inicialización de la cámara a aquí si quieres que la pre-visualización se active al cargar
      // Pero para tu caso actual, está bien que se active con "Iniciar"
    } else {
      statusSpan.classList.add('estado-desconectado');
      text.textContent = 'Cámara desconectada';
    }
  } catch (error) {
    console.error('Error al verificar dispositivos:', error);
    // Mostrar un mensaje más amigable al usuario si hay un error
    const statusSpan = document.getElementById('camera-status');
    const text = document.getElementById('camera-text');
    statusSpan.classList.remove('estado-conectado');
    statusSpan.classList.add('estado-desconectado');
    text.textContent = 'Error al verificar cámara';
  }
}

verificarCamara();
setInterval(verificarCamara, 5000); // Verifica cada 5 segundos si la cámara está conectada

function formatTime(seconds) {
  const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
  const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function startTimer() {
  timerInterval = setInterval(() => {
    elapsedTime++;
    timerDisplay.textContent = formatTime(elapsedTime);
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

function resetTimer() {
  stopTimer();
  elapsedTime = 0;
  timerDisplay.textContent = formatTime(0);
}

btnIniciar.addEventListener('click', async () => {
  if (!stream) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      video.play();
      // Ajusta el tamaño del canvas al video para evitar distorsiones
      video.addEventListener('loadedmetadata', () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
      });
      video.style.display = 'block';
      canvas.style.display = 'none';
      btnIniciar.disabled = true;
      btnDetener.disabled = false;
      btnReset.disabled = false; // Habilitar reset al iniciar

      document.getElementById('video-container').classList.add('expandido');
      intervaloEnvio = setInterval(() => capturarFrame(), 5000); // Envía cada 5 segundos
      startTimer();

      // --- INICIO GRABACIÓN ---
      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      mediaRecorder.ondataavailable = function(e) {
        if (e.data.size > 0) recordedChunks.push(e.data);
      };
      mediaRecorder.onstop = function() {
        // Crear enlace de descarga
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        btnDescargarGrabacion.href = url;
        btnDescargarGrabacion.style.display = "inline-flex";
      };
      mediaRecorder.start();
      // --- FIN INICIO GRABACIÓN ---
    } catch (error) {
      alert("No se pudo acceder a la cámara. Asegúrate de tener una cámara conectada y de dar permisos.");
      console.error("Error al iniciar la cámara:", error);
    }
  }
});

btnDetener.addEventListener('click', () => {
  clearInterval(intervaloEnvio);
  stopTimer();

  // Asegura que el canvas tenga el tamaño correcto antes de dibujar
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.style.display = 'block';
  video.style.display = 'none';

  // --- DETENER GRABACIÓN ---
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  // --- FIN DETENER GRABACIÓN ---

  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
    stream = null;
    btnIniciar.disabled = false;
    btnDetener.disabled = true;
    btnReset.disabled = false; // Mantener reset habilitado o deshabilitar si no hay sesión activa
    document.getElementById('video-container').classList.remove('expandido');
  }
});

// Opcional: Oculta el botón de descarga al resetear
btnReset.addEventListener('click', () => {
  if (intervaloEnvio) clearInterval(intervaloEnvio);
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
    video.srcObject = null;
  }
  stopTimer();
  resetTimer();
  canvas.style.display = 'none';
  video.style.display = 'none';
  document.getElementById('video-container').classList.remove('expandido');
  btnIniciar.disabled = false; // Habilitar iniciar
  btnDetener.disabled = true; // Deshabilitar detener
  btnReset.disabled = true; // Deshabilitar reset después de resetear todo
  btnDescargarGrabacion.style.display = "none";
  // Opcional: limpiar los porcentajes en la UI
  actualizarGraficas({ atentos: 0, distraidos: 0, somnolientos: 0 });
});

function capturarFrame() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8); // 0.8 calidad para reducir tamaño
  // La función toDataURL ya incluye el prefijo "data:image/jpeg;base64,"
  enviarFrameAlBackend(imagenBase64);
}

function enviarFrameAlBackend(imagenBase64) {
  fetch('/api/ia/analizar-imagen/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imagen: imagenBase64 })
  })
  .then(response => {
      if (!response.ok) {
          // Si la respuesta no es OK (ej. 400 Bad Request), lanza un error
          return response.json().then(err => { throw new Error(err.error || 'Error desconocido del servidor'); });
      }
      return response.json();
  })
  .then(data => {
      actualizarGraficas(data);
      console.log("Resultados de IA:", data); // Para depuración
  })
  .catch(error => {
      console.error('Error enviando frame al backend:', error);
      // Podrías mostrar un mensaje de error en la UI aquí
  });
}

function actualizarGraficas(data) {
  // Asegura que los valores sean números válidos
  const atentos = isFinite(Number(data.atentos)) ? Number(data.atentos) : 0;
  const distraidos = isFinite(Number(data.distraidos)) ? Number(data.distraidos) : 0;
  const somnolientos = isFinite(Number(data.somnolientos)) ? Number(data.somnolientos) : 0;

  document.getElementById('barra-atentos').style.width = atentos + '%';
  document.getElementById('barra-distraidos').style.width = distraidos + '%';
  document.getElementById('barra-somnolientos').style.width = somnolientos + '%';

  document.getElementById('porcentaje-atentos').innerText = atentos + '%';
  document.getElementById('porcentaje-distraidos').innerText = distraidos + '%';
  document.getElementById('porcentaje-somnolientos').innerText = somnolientos + '%';

  // Lógica de mostrar/ocultar alerta
  const alerta = document.getElementById('attention-alert');
  if (distraidos >= 50) {
      alerta.classList.remove('hidden');
      alerta.style.display = 'flex';
  } else {
      alerta.classList.add('hidden');
      alerta.style.display = 'none';
  }
}