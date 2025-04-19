from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from django.shortcuts import redirect
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import logging

def home(request):
    gorras = Gorra.objects.filter(disponible=True).order_by('-fecha_creacion')[:12]  # Muestra las 12 más recientes
    context = {
        'gorras': gorras,
        'titulo': 'LinoKappe - Las mejores gorras del mercado'
    }
    return render(request, 'Tienda/base.html', context)


def lista_gorras(request):
    gorras = Gorra.objects.filter(disponible=True)
    return render(request, 'Tienda/lista_gorras.html', {'gorras': gorras})

def detalle_gorra(request, pk):
    gorra = get_object_or_404(Gorra, pk=pk)
    return render(request, 'Tienda/detalle_gorra.html', {'gorra': gorra})

def agregar_gorra(request):
    if request.method == 'POST':
        form = GorraForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = GorraForm()
    return render(request, 'Tienda/agregar_gorra.html', {'form': form})


# Configurar el logger
logger = logging.getLogger(__name__)
# En tu views.py
def validate_image(image):
    try:
        from PIL import Image
        img = Image.open(image)
        img.verify()  # Verificar que es una imagen válida
        image.seek(0)  # Resetear el archivo después de verificar
        return True
    except Exception:
        return False

@csrf_exempt
def crear_pedido(request):
    if request.method == 'POST':
        try:
            form = PedidoForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Validar cada imagen antes de guardar
                for i in range(1, 6):
                    foto_field = f'foto{i}'
                    if foto_field in request.FILES:
                        if not validate_image(request.FILES[foto_field]):
                            return JsonResponse({
                                'success': False,
                                'message': f'La imagen {i} no es válida'
                            }, status=400)
                
                pedido = form.save()
                return JsonResponse({'success': True, 'pedido_id': pedido.id})
                
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
        except Exception as e:
            logger.exception("Error al crear pedido")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)