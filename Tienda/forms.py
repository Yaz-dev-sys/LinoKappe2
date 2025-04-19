from django import forms
from .models import *

class GorraForm(forms.ModelForm):
    class Meta:
        model = Gorra
        fields = ['nombre', 'imagen','imagen2','imagen3','imagen4','imagen5', 'descripcion', 'precio', 'stock', 'disponible']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['gorra_id','email', 'nombre', 'cantidad', 'foto1', 'foto2', 'foto3', 'foto4', 'foto5']