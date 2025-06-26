from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import base64
import numpy as np
import cv2
from monitor_ia.deteccion import analyze_image_for_distraction as analizar_imagen  # Función de IA
from .models import Monitoreo  # Solo importamos Monitoreo
import json
from datetime import datetime
from .forms import ArchivoUploadForm
from .models import SubirArchivo
# Vista para analizar el frame de la cámara
@csrf_exempt
def analizar_frame(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            imagen_base64 = data.get('imagen', '')

            if not imagen_base64:
                return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'No se recibió imagen'}, status=400)

            try:
                # Eliminar el prefijo "data:image/jpeg;base64,"
                if 'data:image' in imagen_base64:
                    header, img_data = imagen_base64.split(',', 1)
                else:
                    img_data = imagen_base64

                # Decodificar los bytes de la imagen
                img_bytes = base64.b64decode(img_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'Error al decodificar la imagen'}, status=400)
            except Exception as e:
                return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': f'Error al procesar la imagen: {str(e)}'}, status=400)

            print("Frame recibido y analizado")
            # Pasa el frame de OpenCV directamente a la función de IA
            resultados = analizar_imagen(frame)

            # Guardar el monitoreo en la base de datos
            Monitoreo.objects.create(
                usuario=request.user,
                atencion=resultados.get('atentos', 0),
                somnolencia=resultados.get('somnolientos', 0),
                distraccion=resultados.get('distraidos', 0),
                fecha=datetime.now()
            )

            return JsonResponse({
                'atentos': resultados.get('atentos', 0),
                'distraidos': resultados.get('distraidos', 0),
                'somnolientos': resultados.get('somnolientos', 0)
            })
        except json.JSONDecodeError:
            return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'JSON inválido'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para mostrar el Dashboard
@login_required
def dashboard(request):
    # Obtener los últimos 30 registros de monitoreo
    monitoreos = Monitoreo.objects.filter(usuario=request.user).order_by('-fecha')[:30]

    # Calcular los promedios
    atencion_promedio = sum(m.atencion for m in monitoreos) / len(monitoreos) if monitoreos else 0
    distraccion_promedio = sum(m.distraccion for m in monitoreos) / len(monitoreos) if monitoreos else 0
    somnolencia_promedio = sum(m.somnolencia for m in monitoreos) / len(monitoreos) if monitoreos else 0

    # Preparar los datos para las gráficas (atención, distracción, somnolencia)
    data_atencion_minutos = [
        {'segundos': i * 5, 'atencion': m.atencion, 'distraccion': m.distraccion, 'somnolencia': m.somnolencia}
        for i, m in enumerate(monitoreos)
    ]

    data_atencion_diaria = [
        {'fecha': m.fecha.strftime('%Y-%m-%d'), 'atencion': m.atencion, 'distraccion': m.distraccion, 'somnolencia': m.somnolencia}
        for m in monitoreos
    ]

    # Pasamos los datos al contexto
    context = {
        'atencion_promedio': round(atencion_promedio),
        'distraccion_promedio': round(distraccion_promedio),
        'somnolencia_promedio': round(somnolencia_promedio),
        'data_atencion_minutos': data_atencion_minutos,
        'data_atencion_diaria': data_atencion_diaria
    }

    return render(request, 'monitor_ia/dashboard.html', context)

@login_required
def subir_archivos(request):
    if request.method == 'POST':
        form = ArchivoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_obj = form.save(commit=False)
            archivo_obj.usuario = request.user  # Asignar el usuario actual
            archivo_obj.save()  # Guardar el archivo
            return redirect('subir_archivos')  # Redirigir después de guardar
    else:
        form = ArchivoUploadForm()  # Formulario vacío para GET

    # Obtener los archivos subidos por el usuario actual
    archivos = SubirArchivo.objects.filter(usuario=request.user).order_by('-fecha_subida')
    return render(request, 'monitor_ia/subir_archivos.html', {
        'form': form,  # Formulario en la plantilla
        'archivos': archivos  # Archivos subidos por el usuario
    })