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
        fields = ['gorra_id', 'email', 'nombre', 'cantidad', 'talla', 'visera', 'color', 
                 'foto1', 'foto2', 'foto3', 'foto4', 'foto5', 'logo_original']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos de imagen no obligatorios
        for i in range(1, 6):
            self.fields[f'foto{i}'].required = False
        self.fields['logo_original'].required = False
        # También puedes hacer opcionales los nuevos campos si es necesario
        self.fields['talla'].required = False
        self.fields['visera'].required = False
        self.fields['color'].required = False