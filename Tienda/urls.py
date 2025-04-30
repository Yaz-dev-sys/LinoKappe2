from django.urls import path
from . import views  # Importa las vistas de la app Tienda

urlpatterns = [
    path('', views.info, name='inicio'),  # Esta es la URL que buscas como 'inicio'
    path('coleccion', views.lista_gorras, name='coleccion'),  # Esta es la URL que buscas como 'inicio'
    path('gorra/<int:pk>/', views.detalle_gorra, name='detalle_gorra'),
    path('agregar/', views.agregar_gorra, name='agregar_gorra'),
    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    path('enviar-correo/', views.enviar_correo, name='enviar_correo'),  # URL para probar el envío de correo
    # Puedes añadir más URLs aquí
]