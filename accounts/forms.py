# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé avec des classes CSS"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    
    error_messages = {
        'invalid_login': (
            "Nom d'utilisateur ou mot de passe incorrect."
        ),
        'inactive': ("Ce compte est désactivé."),
    }