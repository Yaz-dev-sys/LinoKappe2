from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from django.shortcuts import redirect
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import logging
from django.core.mail import send_mail,get_connection
from django.conf import settings
import smtplib
import ssl
import resend
from .forms import PedidoForm


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
    



# Configura la API Key
resend.api_key = "re_762SFCJL_DFxnfjStSnYtdW7bKShPNqd8"  # Tu API KEY aquí

def enviar_correo(request):
    try:
        params = {
            "from": "Acme <onboarding@resend.dev>",
            "to": ["rata6465@gmail.com"],
            "subject": "🚀 ¡Correo enviado exitosamente desde Django!",
            "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                    <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center;">
                        <h1>¡Éxito! 🎉</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p style="font-size: 16px;">Hola 👋,</p>
                        <p style="font-size: 16px;">Este es un <strong>correo de prueba</strong> enviado desde una vista de Django utilizando la API de <em>Resend</em>.</p>
                        <p style="font-size: 16px;">Si estás viendo esto, ¡la integración funciona correctamente! 🧑‍💻</p>
                        <div style="margin-top: 30px; text-align: center;">
                            <a href="https://www.djangoproject.com/" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;">Visita Django</a>
                        </div>
                    </div>
                    <div style="background-color: #f0f0f0; padding: 10px; text-align: center; font-size: 12px; color: #888;">
                        Este correo fue generado automáticamente desde tu proyecto de Django.
                    </div>
                </div>
            """
        }
        
        email = resend.Emails.send(params)
        
        return JsonResponse({'message': 'Correo enviado', 'data': email})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



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
                        
                        if not file.content_type.startswith('image/'):
                            return JsonResponse({
                                'success': False,
                                'message': f'El archivo {file.name} no es una imagen válida'
                            }, status=400)
                        
                        if file.size > 5 * 1024 * 1024:
                            return JsonResponse({
                                'success': False,
                                'message': f'La imagen {file.name} es demasiado grande (máximo 5MB)'
                            }, status=400)
                
                # Validar el logo original si existe
                if 'logo_original' in request.FILES:
                    logo_file = request.FILES['logo_original']
                    if not logo_file.content_type.startswith('image/'):
                        return JsonResponse({
                            'success': False,
                            'message': 'El archivo del logo no es una imagen válida'
                        }, status=400)
                    
                    if logo_file.size > 5 * 1024 * 1024:
                        return JsonResponse({
                            'success': False,
                            'message': 'El logo es demasiado grande (máximo 5MB)'
                        }, status=400)
                
                # Guardar el pedido
                pedido = form.save()
                
                # Enviar correo con los datos del pedido
                try:
                    # Obtener todos los campos del pedido como diccionario
                    datos_pedido = {
                        'ID': pedido.id,
                        'Nombre': pedido.nombre,
                        'Email': pedido.email,
                        'Cantidad': pedido.cantidad,
                        'Talla': pedido.get_talla_display() if pedido.talla else 'No especificada',
                        'Visera': pedido.get_visera_display() if pedido.visera else 'No especificada',
                        'Color': pedido.color if pedido.color else 'No especificado',
                    }
                    
                    # Añadir los demás campos del modelo Pedido si son necesarios
                    if hasattr(pedido, 'direccion'):
                        datos_pedido['Dirección'] = pedido.direccion
                    if hasattr(pedido, 'producto'):
                        datos_pedido['Producto'] = pedido.producto
                    if hasattr(pedido, 'fecha_pedido'):
                        datos_pedido['Fecha de pedido'] = pedido.fecha_pedido
                    
                    # Crear HTML para el correo
                    filas_html = ""
                    for campo, valor in datos_pedido.items():
                        filas_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">{campo}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{valor}</td>
                        </tr>
                        """
                    
                        # Enviar correo con Resend
                        params = {
                            "from": "Pedidos <onboarding@resend.dev>",
                            "to": ["linokappepedido@gmail.com"],  # Cambia a tu correo o el de destino
                            "subject": f"🛒 Nuevo Pedido #{pedido.id}",
                            "html": f"""
                            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                                <div style="background-color: #4361EE; color: white; padding: 20px; text-align: center;">
                                    <h1>¡Nuevo Pedido Recibido! 🎉</h1>
                                </div>
                                <div style="padding: 20px;">
                                    <p style="font-size: 16px;">Se ha registrado un nuevo pedido con la siguiente información:</p>
                                    
                                    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                                        {filas_html}
                                    </table>
                                    
                                    <p style="margin-top: 20px; font-size: 14px;">Para ver las imagenes del pedido favor de consultar el Panel de Administración.</p>
                                </div>
                                <div style="background-color: #f0f0f0; padding: 10px; text-align: center; font-size: 12px; color: #888;">
                                    Este correo fue generado automáticamente por el sistema de pedidos.
                                </div>
                            </div>
                            """
                        }
                        
                        resend.Emails.send(params)
                        logger.info(f"Correo enviado para pedido #{pedido.id}")
                        
                    
                except Exception as e:
                    logger.error(f"Error al enviar correo: {str(e)}")
                    # No detenemos el proceso si falla el envío de correo
                
                return JsonResponse({
                    'success': True,
                    'pedido_id': pedido.id,
                    'message': 'Pedido creado correctamente'
                })
            
            # Errores de formulario
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
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)

