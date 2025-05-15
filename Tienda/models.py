from django.db import models
from django.contrib.auth.models import User

class Gorra(models.Model):
    nombre = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='gorras/')  # Se guardará en media/gorras/
    imagen2 = models.ImageField(upload_to='gorras/', null=True, blank=True)
    imagen3 = models.ImageField(upload_to='gorras/', null=True, blank=True)
    imagen4 = models.ImageField(upload_to='gorras/', null=True, blank=True)
    imagen5 = models.ImageField(upload_to='gorras/', null=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    


class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()

    def __str__(self):
        return self.usuario.username



class Pedido(models.Model):
    ESTADOS = [
        ('P', 'Pendiente'),
        ('C', 'Completado'),
        ('X', 'Cancelado'),
    ]
    
    # Opciones para los nuevos campos
    TALLAS = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    
    TIPOS_VISERA = [
        ('PLANA', 'Plana'),
        ('CURVA', 'Curva'),
    ]
    
    gorra_id = models.ForeignKey(Gorra, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    
    # Nuevos campos
    talla = models.CharField(max_length=3, choices=TALLAS, null=True, blank=True)
    visera = models.CharField(max_length=5, choices=TIPOS_VISERA, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    
    foto1 = models.ImageField(upload_to='pedidos/', default='pedidos/default.jpg')
    foto2 = models.ImageField(upload_to='pedidos/', null=True, blank=True)
    foto3 = models.ImageField(upload_to='pedidos/', null=True, blank=True)
    foto4 = models.ImageField(upload_to='pedidos/', null=True, blank=True)
    foto5 = models.ImageField(upload_to='pedidos/', null=True, blank=True)
    logo_original = models.ImageField(upload_to='logos/', null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre}"