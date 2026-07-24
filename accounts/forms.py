# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User


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


class InscriptionForm(forms.Form):
    ferme_nom = forms.CharField(max_length=255, label="Nom de la ferme")
    ferme_localisation = forms.CharField(max_length=255, label="Localisation")
    ferme_email = forms.EmailField(label="Email de la ferme")
    ferme_telephone = forms.CharField(max_length=20, required=False, label="Téléphone (optionnel)")

    admin_username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        validators=[UnicodeUsernameValidator(
            message="Nom d'utilisateur invalide. Lettres, chiffres et @/./+/-/_ uniquement, sans espace.",
        )],
        help_text="Lettres, chiffres et @/./+/-/_ uniquement, sans espace.",
    )
    admin_email = forms.EmailField(label="Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    admin_password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    def clean_admin_password(self):
        password = self.cleaned_data.get('admin_password')
        utilisateur_temporaire = User(
            username=self.data.get('admin_username', ''),
            email=self.data.get('admin_email', ''),
        )
        try:
            validate_password(password, user=utilisateur_temporaire)
        except DjangoValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        password_confirm = cleaned_data.get('admin_password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('admin_password_confirm', "Les mots de passe ne correspondent pas.")
        return cleaned_data
