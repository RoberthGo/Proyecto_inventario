from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory

from .models import Cliente, Inventario, Ropa


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class RopaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    class Meta:
        model = Ropa
        fields = (
            'modelo',
            'descripcion',
            'tipo',
            'talla',
            'marca',
            'precio',
            'proveedor',
        )
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }


class VentaForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.none(),
        empty_label=None,
        label='Cliente',
    )

    def __init__(self, *args, clientes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = clientes if clientes is not None else Cliente.objects.all()
        self.fields['cliente'].widget.attrs['class'] = 'for m-select'


class VentaItemForm(forms.Form):
    inventario = forms.ModelChoiceField(
        queryset=Inventario.objects.none(),
        label='Producto y color',
        empty_label='Selecciona un producto',
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label='Cantidad',
        widget=forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
    )

    def __init__(self, *args, inventarios=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = inventarios if inventarios is not None else Inventario.objects.none()
        self.fields['inventario'].queryset = queryset
        self.fields['inventario'].widget.attrs['class'] = 'form-select'


class BaseVentaItemFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        inventarios = [
            form.cleaned_data['inventario']
            for form in self.forms
            if form.cleaned_data and form.cleaned_data.get('inventario')
        ]
        if len(inventarios) != len(set(inventario.pk for inventario in inventarios)):
            raise ValidationError('No puedes repetir productos dentro de la misma venta.')


VentaItemFormSet = formset_factory(
    VentaItemForm,
    formset=BaseVentaItemFormSet,
    extra=1,
    max_num=20,
    validate_max=True,
)
