from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Animal

FORM_FIELD_CLASS = 'form-field'


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': "Mot de passe"
        })
    )


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['nom', 'numero_identification', 'espece', 'sexe', 'date_naissance', 'lot', 'statut', 'photo', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Nom de l\'animal'
            }),
            'numero_identification': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Numéro d\'identification unique'
            }),
            'espece': forms.Select(attrs={
                'class': FORM_FIELD_CLASS
            }),
            'sexe': forms.Select(attrs={
                'class': FORM_FIELD_CLASS
            }),
            'date_naissance': forms.DateInput(attrs={
                'type': 'date',
                'class': FORM_FIELD_CLASS
            }),
            'lot': forms.TextInput(attrs={
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Lot ou groupe'
            }),
            'statut': forms.Select(attrs={
                'class': FORM_FIELD_CLASS
            }),
            'photo': forms.FileInput(attrs={
                'class': FORM_FIELD_CLASS,
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'class': FORM_FIELD_CLASS,
                'placeholder': 'Notes supplémentaires...'
            }),
        }
