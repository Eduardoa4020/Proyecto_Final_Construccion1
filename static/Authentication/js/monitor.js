  let stream = null;
  let intervaloEnvio = null;
  let timerInterval = null;
  let elapsedTime = 0;
  
  const video = document.getElementById('video');
  const canvas = document.getElementById('snapshot');
  const context = canvas.getContext('2d');
  const btnIniciar = document.getElementById('start-monitoring');
  const btnDetener = document.getElementById('stop-monitoring');
  const btnReset = document.getElementById('reset-monitoring');
  const alerta = document.getElementById('attention-alert');
  const timerDisplay = document.getElementById('session-timer');

  async function verificarCamara() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hayCamara = devices.some(device => device.kind === 'videoinput');

      const statusSpan = document.getElementById('camera-status');
      const icon = document.getElementById('camera-icon');
      const text = document.getElementById('camera-text');

      // Elimina ambas clases para resetear el estado
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
    }
  }
  verificarCamara();
  setInterval(verificarCamara, 1000);


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
        video.style.display = 'block';
        canvas.style.display = 'none';
        btnIniciar.disabled = true;
        btnDetener.disabled = false;
  
        document.getElementById('video-container').classList.add('expandido');
        intervaloEnvio = setInterval(() => capturarFrame(), 5000);
        startTimer();
      } catch (error) {
        alert("No se pudo acceder a la cámara.");
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
  
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      video.srcObject = null;
      stream = null;
      btnIniciar.disabled = false;
      btnDetener.disabled = true;
      document.getElementById('video-container').classList.remove('expandido');
    }
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
  });
  
  function capturarFrame() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imagenBase64 = canvas.toDataURL('image/jpeg');
    enviarFrameAlBackend(imagenBase64);
  }
  
  function enviarFrameAlBackend(imagenBase64) {
    fetch('/api/ia/analizar-imagen/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imagen: imagenBase64 })
    })
    .then(response => response.json())
    .then(data => actualizarGraficas(data))
    .catch(error => console.error('Error enviando frame al backend:', error));
  }
  
  function actualizarGraficas(data) {
    // Actualizar las barras y porcentajes
    document.getElementById('barra-atentos').style.width = data.atentos + '%';
    document.getElementById('barra-distraidos').style.width = data.distraidos + '%';
    document.getElementById('barra-somnolientos').style.width = data.somnolientos + '%';

    document.getElementById('porcentaje-atentos').innerText = data.atentos + '%';
    document.getElementById('porcentaje-distraidos').innerText = data.distraidos + '%';
    document.getElementById('porcentaje-somnolientos').innerText = data.somnolientos + '%';

    // Lógica de mostrar/ocultar alerta
    const alerta = document.getElementById('attention-alert');
    const porcentajeDistraidos = parseFloat(data.distraidos);

    if (!isNaN(porcentajeDistraidos) && porcentajeDistraidos >= 50) {
        alerta.classList.remove('hidden');
        alerta.style.display = 'flex';
    } else {
        alerta.classList.add('hidden');
        alerta.style.display = 'none';
    }
    }

function guardarNombreClase() {
  const input = document.getElementById('nombre-clase');
  const nombre = input.value.trim();

  if (!nombre) {
    alert("⚠ Debes ingresar un nombre para la clase.");
    return;
  }

  if (nombre.length > 30) {
    alert("⚠ El nombre no puede tener más de 30 caracteres.");
    return;
  }

  // Aquí puedes guardar en localStorage o enviarlo a tu backend si deseas persistencia
  console.log("Nombre de clase guardado:", nombre);
  alert("✅ Nombre de clase guardado: " + nombre);
}
