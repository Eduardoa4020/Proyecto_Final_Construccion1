// monitor.js
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
const alerta = document.getElementById('attention-alert');
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
    } else {
      statusSpan.classList.add('estado-desconectado');
      text.textContent = 'Cámara desconectada';
    }
  } catch (error) {
    console.error('Error al verificar dispositivos:', error);
    const statusSpan = document.getElementById('camera-status');
    const text = document.getElementById('camera-text');
    statusSpan.classList.remove('estado-conectado');
    statusSpan.classList.add('estado-desconectado');
    text.textContent = 'Error al verificar cámara';
  }
}

verificarCamara();
setInterval(verificarCamara, 5000);

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
      video.addEventListener('loadedmetadata', () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
      });
      video.style.display = 'block';
      canvas.style.display = 'none';
      btnIniciar.disabled = true;
      btnDetener.disabled = false;
      btnReset.disabled = false;

      document.getElementById('video-container').classList.add('expandido');
      intervaloEnvio = setInterval(() => capturarFrame(), 5000);
      startTimer();

      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      mediaRecorder.ondataavailable = function(e) {
        if (e.data.size > 0) {
          recordedChunks.push(e.data);
        }
      };
      mediaRecorder.onstop = function() {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        btnDescargarGrabacion.href = url;
        btnDescargarGrabacion.style.display = "inline-flex";
      };
      mediaRecorder.start();
    } catch (error) {
      alert("No se pudo acceder a la cámara. Asegúrate de tener una cámara conectada y de dar permisos.");
      console.error("Error al iniciar la cámara:", error);
    }
  }
});

btnDetener.addEventListener('click', () => {
  clearInterval(intervaloEnvio);
  stopTimer();

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.style.display = 'block';
  video.style.display = 'none';

  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }

  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
    stream = null;
    btnIniciar.disabled = false;
    btnDetener.disabled = true;
    btnReset.disabled = false;
    document.getElementById('video-container').classList.remove('expandido');
  }

  const atencionTotal = totalFrames > 0 ? Math.round(totalAtencion / totalFrames) : 0;
  const somnolenciaTotal = totalFrames > 0 ? Math.round(totalSomnolencia / totalFrames) : 0;
  const distraccionTotal = totalFrames > 0 ? Math.round(totalDistraccion / totalFrames) : 0;

  console.log("Enviando reporte:", atencionTotal, somnolenciaTotal, distraccionTotal);

  guardarReporteHistorico(atencionTotal, somnolenciaTotal, distraccionTotal);

  totalAtencion = 0;
  totalSomnolencia = 0;
  totalDistraccion = 0;
  totalFrames = 0;
});

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
  btnIniciar.disabled = false;
  btnDetener.disabled = true;
  btnReset.disabled = true;
  btnDescargarGrabacion.style.display = "none";
  actualizarGraficas({ atentos: 0, distraidos: 0, somnolientos: 0 });
});

function capturarFrame() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8);
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
          return response.json().then(err => { throw new Error(err.error || 'Error desconocido del servidor'); });
      }
      return response.json();
  })
  .then(data => {
      actualizarGraficas(data);
      console.log("Resultados de IA:", data);
  })
  .catch(error => {
      console.error('Error enviando frame al backend:', error);
  });
}

let totalAtencion = 0;
let totalSomnolencia = 0;
let totalDistraccion = 0;
let totalFrames = 0;

function actualizarGraficas(data) {
  const atentos = isFinite(Number(data.atentos)) ? Number(data.atentos) : 0;
  const distraidos = isFinite(Number(data.distraidos)) ? Number(data.distraidos) : 0;
  const somnolientos = isFinite(Number(data.somnolientos)) ? Number(data.somnolientos) : 0;

  document.getElementById('barra-atentos').style.width = atentos + '%';
  document.getElementById('barra-distraidos').style.width = distraidos + '%';
  document.getElementById('barra-somnolientos').style.width = somnolientos + '%';

  document.getElementById('porcentaje-atentos').innerText = atentos + '%';
  document.getElementById('porcentaje-distraidos').innerText = distraidos + '%';
  document.getElementById('porcentaje-somnolientos').innerText = somnolientos + '%';

  totalAtencion += atentos;
  totalSomnolencia += somnolientos;
  totalDistraccion += distraidos;
  totalFrames += 1;
}

function guardarReporteHistorico(atencionTotal, somnolenciaTotal, distraccionTotal) {
    fetch('/api/ia/guardar_reporte_historico/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            atencion: atencionTotal,
            somnolencia: somnolenciaTotal,
            distraccion: distraccionTotal
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Error desconocido del servidor'); });
        }
        return response.json();
    })
    .then(data => {
        console.log("Respuesta del backend:", data);
        if (data.status === "ok") {
            alert("Reporte guardado correctamente.");
        } else {
            alert("Error al guardar el reporte: " + (data.error || "Error desconocido"));
        }
    })
    .catch(error => {
        console.error("Error al guardar el reporte:", error);
        alert("Error al guardar el reporte: " + error.message);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}