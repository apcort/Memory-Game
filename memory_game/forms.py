from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistroForm(UserCreationForm):
    """
    Formulario de registro
    """

    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['username', 'email', 'password1', 'password2'])
        for campo in self.fields.values():
            campo.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe una cuenta registrada con este correo.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario


class LoginForm(forms.Form):
    """Formulario inicio de sesion (usuario + contraseña)."""

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
