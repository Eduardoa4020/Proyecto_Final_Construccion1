# monitor_ia/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import numpy as np
import cv2
from monitor_ia.deteccion import analizar_imagen
from django.contrib.auth.decorators import login_required
from .forms import ArchivoUploadForm
from .models import SubirArchivo

@login_required
def subir_archivos(request):
    if request.method == 'POST':
        form = ArchivoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_obj = form.save(commit=False)
            archivo_obj.usuario = request.user
            archivo_obj.save()
            return redirect('subir_archivos')  # Cambia por el nombre real de tu url
    else:
        form = ArchivoUploadForm()

    archivos = SubirArchivo.objects.filter(usuario=request.user).order_by('-fecha_subida')
    return render(request, 'monitor_ia/subir_archivos.html', {
        'form': form,
        'archivos': archivos
    })

@csrf_exempt
def analizar_frame(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        if 'imagen' not in data:
            # Siempre devuelve las claves esperadas
            return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'No se recibió imagen'}, status=400)

        import json
        data_json = json.loads(data)
        imagen_base64 = data_json.get('imagen', '')
        if not imagen_base64:
            return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'Imagen vacía'}, status=400)

        try:
            header, encoded = imagen_base64.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': str(e)}, status=400)

        print("Frame recibido y analizado")

        resultados = analizar_imagen(frame)
        # Asegura que siempre existan las claves
        return JsonResponse({
            'atentos': resultados.get('atentos', 0),
            'distraidos': resultados.get('distraidos', 0),
            'somnolientos': resultados.get('somnolientos', 0)
        })
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
