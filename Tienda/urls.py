from django.urls import path
from . import views  # Importa las vistas de la app Tienda

urlpatterns = [
    path('', views.lista_gorras, name='inicio'),  # Esta es la URL que buscas como 'inicio'
    path('gorra/<int:pk>/', views.detalle_gorra, name='detalle_gorra'),
    path('agregar/', views.agregar_gorra, name='agregar_gorra'),
    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    # Puedes añadir más URLs aquí
]