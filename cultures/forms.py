# cultures/forms.py
from django import forms
from django.utils import timezone
from .models import Parcelle, Culture, CultureParcelle, ActiviteAgricole


class ParcelleForm(forms.ModelForm):
    """Formulaire pour créer/modifier une parcelle"""
    
    class Meta:
        model = Parcelle
        fields = ['nom', 'superficie', 'type_sol', 'localisation']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Champ Nord, Parcelle A'
            }),
            'superficie': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'type_sol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Argileux, Sableux, Limoneux'
            }),
            'localisation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Près de la rivière, Zone est'
            }),
        }
    
    def clean_superficie(self):
        superficie = self.cleaned_data.get('superficie')
        if superficie and superficie <= 0:
            raise forms.ValidationError("La superficie doit être supérieure à 0 hectare.")
        return superficie


class CultureParcelleForm(forms.ModelForm):
    """Formulaire pour associer une culture à une parcelle"""
    
    class Meta:
        model = CultureParcelle
        fields = ['parcelle', 'culture', 'date_semis', 'date_recolte_prevue', 'date_recolte_reelle', 'rendement', 'notes']
        widgets = {
            'parcelle': forms.Select(attrs={'class': 'form-control'}),
            'culture': forms.Select(attrs={'class': 'form-control'}),
            'date_semis': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_recolte_prevue': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_recolte_reelle': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'rendement': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur la culture...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les parcelles par ferme de l'utilisateur
            self.fields['parcelle'].queryset = Parcelle.objects.filter(ferme=user.ferme)
        
        # Ajouter une classe CSS à tous les champs
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'


class ActiviteAgricoleForm(forms.ModelForm):
    """Formulaire pour ajouter une activité agricole"""
    
    class Meta:
        model = ActiviteAgricole
        fields = ['culture_parcelle', 'type', 'date', 'description', 'intrants_utilises']
        widgets = {
            'culture_parcelle': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description de l\'activité...'
            }),
            'intrants_utilises': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Engrais NPK 15-15-15, 50kg'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les cultures parcelles par ferme de l'utilisateur
            self.fields['culture_parcelle'].queryset = CultureParcelle.objects.filter(
                parcelle__ferme=user.ferme
            )
        
        # Ajouter une classe CSS à tous les champs
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Date par défaut = aujourd'hui
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()