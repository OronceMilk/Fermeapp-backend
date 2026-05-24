# cheptel/forms.py
from django import forms
from django.utils import timezone
from .models import Animal, Espece, LotPondeuses, Produit, Traitement, RapportJournalier


# ==============================
# FORMULAIRE ANIMAL
# ==============================
class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['identifiant', 'nom', 'espece', 'lot', 'race', 'sexe', 
                 'date_naissance', 'statut', 'photo', 'notes']
        widgets = {
            'identifiant': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PO-001, LAP-005'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom optionnel de l\'animal'
            }),
            'espece': forms.Select(attrs={'class': 'form-control'}),
            'lot': forms.Select(attrs={'class': 'form-control'}),
            'race': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Race de l\'animal'
            }),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer l'utilisateur passé en paramètre
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remplir les choix dynamiquement
        self.fields['espece'].queryset = Espece.objects.all()
        
        # Filtrer les lots par ferme de l'utilisateur
        if self.user:
            self.fields['lot'].queryset = LotPondeuses.objects.filter(ferme=self.user.ferme)
        else:
            self.fields['lot'].queryset = LotPondeuses.objects.all()
        
        # Ajouter des classes CSS
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        espece = cleaned_data.get('espece')
        lot = cleaned_data.get('lot')
        
        # Vérifier que l'espèce correspond au lot
        if espece and lot and lot.espece != espece:
            raise forms.ValidationError(
                f"L'espèce '{espece.nom}' ne correspond pas au lot '{lot.nom}' (espèce: {lot.espece.nom})"
            )
        
        return cleaned_data


# ==============================
# FORMULAIRE LOT
# ==============================
class LotForm(forms.ModelForm):
    class Meta:
        model = LotPondeuses
        fields = ['nom', 'espece', 'nombre_sujets', 'date_mise_en_place', 'race', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Lot A - Pondeuses 2026'
            }),
            'espece': forms.Select(attrs={'class': 'form-control'}),
            'nombre_sujets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Nombre d\'animaux dans le lot'
            }),
            'date_mise_en_place': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'race': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Isa Brown, Rhode Island...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Informations supplémentaires sur le lot...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer l'utilisateur passé en paramètre
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['espece'].queryset = Espece.objects.all()
        self.fields['espece'].empty_label = "-- Sélectionner une espèce --"
    
    def clean_nombre_sujets(self):
        nombre = self.cleaned_data.get('nombre_sujets')
        if nombre and nombre <= 0:
            raise forms.ValidationError("Le nombre de sujets doit être supérieur à 0.")
        return nombre


# ==============================
# FORMULAIRE RAPPORT JOURNALIER
# ==============================
class RapportJournalierForm(forms.ModelForm):
    class Meta:
        model = RapportJournalier
        fields = ['date', 'nombre_morts', 'oeufs_pondus', 'aliment_kg', 'eau_litres', 'sujets_malades', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nombre_morts': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '0'
            }),
            'oeufs_pondus': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '0'
            }),
            'aliment_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.1,
                'placeholder': '0.0'
            }),
            'eau_litres': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.1,
                'placeholder': '0.0'
            }),
            'sujets_malades': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer la ferme passée en paramètre
        self.ferme = kwargs.pop('ferme', None)
        super().__init__(*args, **kwargs)
        
        # Rendre la date optionnelle (par défaut = aujourd'hui)
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        
        if date and date > timezone.now().date():
            raise forms.ValidationError("La date ne peut pas être dans le futur.")
        
        return cleaned_data


# ==============================
# FORMULAIRE TRAITEMENT
# ==============================
class TraitementForm(forms.ModelForm):
    class Meta:
        model = Traitement
        fields = ['animal', 'type', 'date', 'produit', 'dose', 'rappel_le', 'notes']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'dose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2ml, 5mg/kg'}),
            'rappel_le': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer l'utilisateur passé en paramètre
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les animaux par ferme de l'utilisateur
            self.fields['animal'].queryset = Animal.objects.filter(ferme=user.ferme)
            # Filtrer les produits (si besoin par ferme plus tard)
            self.fields['produit'].queryset = Produit.objects.all()