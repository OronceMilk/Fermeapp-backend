from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'categorie', 'montant', 'date', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
            'montant': forms.NumberInput(attrs={'inputmode': 'decimal', 'step': '0.01', 'min': '0'}),
        }