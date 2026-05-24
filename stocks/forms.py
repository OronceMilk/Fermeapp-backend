# stocks/forms.py
from django import forms
from django.utils import timezone
from decimal import Decimal
from .models import ProduitStock, MouvementStock


class ProduitStockForm(forms.ModelForm):
    """Formulaire pour créer/modifier un produit en stock"""
    
    class Meta:
        model = ProduitStock
        fields = ['nom', 'unite', 'emplacement', 'quantite_actuelle', 'seuil_alerte', 
                  'fournisseur_principal', 'prix_moyen_unitaire']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Aliment poule ponte, Vaccin Marek...'
            }),
            'unite': forms.Select(attrs={'class': 'form-control'}),
            'emplacement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Magasin principal, Réfrigérateur...'
            }),
            'quantite_actuelle': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'seuil_alerte': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'fournisseur_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: AgroBénin, FermePlus...'
            }),
            'prix_moyen_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if nom:
            nom = nom.strip().capitalize()
        return nom
    
    def clean_quantite_actuelle(self):
        quantite = self.cleaned_data.get('quantite_actuelle')
        if quantite is not None and quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return quantite
    
    def clean_seuil_alerte(self):
        seuil = self.cleaned_data.get('seuil_alerte')
        if seuil is not None and seuil < 0:
            raise forms.ValidationError("Le seuil d'alerte ne peut pas être négatif.")
        return seuil


class EntreeStockForm(forms.ModelForm):
    """Formulaire pour ajouter une entrée de stock (achat)"""
    
    class Meta:
        model = MouvementStock
        fields = ['produit', 'quantite', 'date', 'reference', 'prix_unitaire', 'motif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Facture N°, Bon de commande...'
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Raison de l\'entrée en stock...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les produits par ferme
            self.fields['produit'].queryset = ProduitStock.objects.filter(ferme=user.ferme)
        
        # Date par défaut = aujourd'hui
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        quantite = cleaned_data.get('quantite')
        
        if quantite is not None and quantite <= 0:
            self.add_error('quantite', "La quantité doit être strictement positive.")
        
        return cleaned_data


class SortieStockForm(forms.ModelForm):
    """Formulaire pour ajouter une sortie de stock (consommation)"""
    
    class Meta:
        model = MouvementStock
        fields = ['produit', 'quantite', 'date', 'reference', 'motif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bon de sortie, Consommation...'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Raison de la sortie (ex: alimentation animaux, traitement...)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrer les produits par ferme
            self.fields['produit'].queryset = ProduitStock.objects.filter(ferme=user.ferme)
        
        # Date par défaut = aujourd'hui
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()
    
    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        produit = self.cleaned_data.get('produit')
        
        if quantite is not None and quantite <= 0:
            raise forms.ValidationError("La quantité doit être strictement positive.")
        
        if produit and quantite and quantite > produit.quantite_actuelle:
            raise forms.ValidationError(
                f"Stock insuffisant. Disponible: {produit.quantite_actuelle} {produit.get_unite_display()}"
            )
        
        return quantite


class MouvementFiltreForm(forms.Form):
    """Formulaire de filtrage pour la liste des mouvements"""
    
    produit = forms.ModelChoiceField(
        queryset=ProduitStock.objects.none(),
        required=False,
        label="Produit",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    type = forms.ChoiceField(
        choices=[('', 'Tous')] + list(MouvementStock.TYPE_CHOICES),
        required=False,
        label="Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_debut = forms.DateField(
        required=False,
        label="Du",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_fin = forms.DateField(
        required=False,
        label="Au",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['produit'].queryset = ProduitStock.objects.filter(ferme=user.ferme)