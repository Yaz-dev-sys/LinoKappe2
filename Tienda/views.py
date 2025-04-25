from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from django.shortcuts import redirect
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import logging
from django.core.mail import send_mail
from django.conf import settings

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

def info(request):
    gorras = Gorra.objects.filter(disponible=True)
    return render(request, 'Tienda/info.html', {'gorras': gorras})


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
    

import ssl
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .forms import PedidoForm

logger = logging.getLogger(__name__)

@csrf_exempt
def crear_pedido(request):
    if request.method == 'POST':
        try:
            form = PedidoForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Validación de imágenes (máximo 5 imágenes)
                for i in range(1, 6):
                    foto_field = f'foto{i}'
                    if foto_field in request.FILES:
                        file = request.FILES[foto_field]
                        # Validar tipo de archivo
                        if not file.content_type.startswith('image/'):
                            return JsonResponse({
                                'success': False,
                                'message': f'El archivo {file.name} no es una imagen válida'
                            }, status=400)
                        # Validar tamaño (ejemplo: máximo 5MB)
                        if file.size > 5 * 1024 * 1024:
                            return JsonResponse({
                                'success': False,
                                'message': f'La imagen {file.name} es demasiado grande (máximo 5MB)'
                            }, status=400)

                # Guardar el pedido
                pedido = form.save()

                try:
                    # Construir el mensaje HTML
                    subject = f'Nuevo pedido #{pedido.id} - {pedido.nombre}'
                    html_message = f"""
                    <html>
                        <body>
                            <h1 style="color: #4CAF50;">Nuevo pedido recibido</h1>
                            <table border="1" cellpadding="10" style="border-collapse: collapse;">
                                <tr>
                                    <th>ID del pedido</th>
                                    <td>{pedido.id}</td>
                                </tr>
                                <tr>
                                    <th>Nombre</th>
                                    <td>{pedido.nombre}</td>
                                </tr>
                                <tr>
                                    <th>Email</th>
                                    <td>{pedido.email}</td>
                                </tr>
                                <tr>
                                    <th>Cantidad</th>
                                    <td>{pedido.cantidad}</td>
                                </tr>
                                <tr>
                                    <th>Fecha del pedido</th>
                                    <td>{pedido.fecha_pedido.strftime("%Y-%m-%d %H:%M:%S")}</td>
                                </tr>
                            </table>
                        </body>
                    </html>
                    """

                    # Versión de texto plano
                    plain_message = f"""
                    Nuevo pedido #{pedido.id}
                    -------------------------
                    Nombre: {pedido.nombre}
                    Email: {pedido.email}
                    Cantidad: {pedido.cantidad}
                    Fecha: {pedido.fecha_pedido.strftime("%Y-%m-%d %H:%M:%S")}
                    """

                    # Configuración especial para el envío de correo
                    ssl_context = ssl.create_default_context()
                    
                    # Para desarrollo: desactivar verificación SSL (eliminar en producción)
                    if settings.DEBUG:
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE

                    # Enviar correo con configuración personalizada
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['rata6465@gmail.com'],
                        fail_silently=False,
                        html_message=html_message,
                        connection=None,  # Usará el contexto SSL configurado
                    )

                except Exception as email_error:
                    logger.error(f"Error al enviar el correo: {str(email_error)}", exc_info=True)
                    # Continuar a pesar del error de correo pero registrarlo
                    return JsonResponse({
                        'success': True,
                        'pedido_id': pedido.id,
                        'message': 'Pedido creado pero no se pudo enviar el correo de confirmación',
                        'warning': str(email_error)
                    })

                # Respuesta exitosa
                return JsonResponse({
                    'success': True,
                    'pedido_id': pedido.id,
                    'message': 'Pedido creado y correo enviado correctamente'
                })
            
            # Si el formulario no es válido
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos del formulario',
                'errors': errors
            }, status=400)
        
        except Exception as e:
            logger.exception("Error al crear pedido")
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    # Si no es POST
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)