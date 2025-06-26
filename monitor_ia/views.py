from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64 # Usaremos este base64, no el de cv2
import numpy as np
import cv2
from monitor_ia.deteccion import analyze_image_for_distraction as analizar_imagen # Importa con el alias correcto
from django.contrib.auth.decorators import login_required
from .forms import ArchivoUploadForm
from .models import SubirArchivo, ReporteHistorico
import json

@login_required
def subir_archivos(request):
    if request.method == 'POST':
        form = ArchivoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_obj = form.save(commit=False)
            archivo_obj.usuario = request.user
            archivo_obj.save()
            return redirect('subir_archivos')  # Cambia por el nombre real de tu url si es diferente
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
                
                # Decodificar los bytes usando la librería base64 de Python
                img_bytes = base64.b64decode(img_data) 
                nparr = np.frombuffer(img_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'Error al decodificar la imagen'}, status=400)
            except Exception as e:
                # Captura errores específicos de decodificación o procesamiento de imagen
                return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': f'Error al procesar la imagen: {str(e)}'}, status=400)

            print("Frame recibido y analizado")
            # Pasa el frame de OpenCV directamente a la función de IA
            resultados = analizar_imagen(frame) 
            
            return JsonResponse({
                'atentos': resultados.get('atentos', 0),
                'distraidos': resultados.get('distraidos', 0),
                'somnolientos': resultados.get('somnolientos', 0)
            })
        except json.JSONDecodeError:
            # Captura errores si el cuerpo de la solicitud no es JSON válido
            return JsonResponse({'atentos': 0, 'distraidos': 0, 'somnolientos': 0, 'error': 'JSON inválido'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def atencion_data(request):
    # Devuelve los últimos 30 registros para las gráficas
    reportes = ReporteHistorico.objects.order_by('-timestamp')[:30][::-1]
    data = [
        {"minuto": i*10, "atencion": r.atentos}
        for i, r in enumerate(reportes)
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def guardar_reporte_historico(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            atencion = int(data.get('atencion', 0))
            somnolencia = int(data.get('somnolencia', 0))
            distraccion = int(data.get('distraccion', 0))

            # Validar los datos
            if not (0 <= atencion <= 100 and 0 <= somnolencia <= 100 and 0 <= distraccion <= 100):
                return JsonResponse({'status': 'error', 'error': 'Valores inválidos'}, status=400)

            # Guardar el reporte en el modelo ReporteHistorico
            reporte = ReporteHistorico(
                usuario=request.user,
                atentos=atencion,
                somnolientos=somnolencia,
                distraidos=distraccion
            )
            reporte.save()

            return JsonResponse({'status': 'ok', 'message': 'Reporte guardado correctamente'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': f'Error al guardar el reporte: {str(e)}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'error': 'Método no permitido'}, status=405)