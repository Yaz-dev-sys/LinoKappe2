from django.contrib import admin
# Register your models here.

from .models import *  # Asegúrate de importar tu modelo

# Registro básico de todos los modelos
admin.site.register(Gorra)
admin.site.register(Cliente)
admin.site.register(Pedido)
