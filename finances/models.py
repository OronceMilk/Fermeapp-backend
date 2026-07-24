from datetime import date
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Ferme, User


class Transaction(models.Model):
    """
    Mouvement financier qui n'a AUCUNE autre représentation dans le système.

    Frontière stricte avec stocks.MouvementStock :
    - Un achat de produit stocké (aliment, vaccin, semence...) reste exclusivement
      un MouvementStock (type ENTREE) — ne JAMAIS le ressaisir ici, sous peine de
      double-comptage dans dashboard/services/finance_service.py::get_finances().
    - Transaction couvre uniquement : ventes (aucune trace ailleurs dans le système),
      et dépenses hors-stock (salaires, vétérinaire, location, transport...).
    """

    TYPE_CHOICES = [
        ('DEPENSE', 'Dépense'),
        ('RECETTE', 'Recette'),
    ]

    CATEGORIES_DEPENSE = ['SALAIRE', 'VETERINAIRE', 'LOCATION', 'TRANSPORT', 'AUTRE_DEPENSE']
    CATEGORIES_RECETTE = ['VENTE_ANIMAUX', 'VENTE_OEUFS', 'VENTE_CULTURES', 'AUTRE_RECETTE']

    CATEGORIE_CHOICES = [
        ('SALAIRE', 'Salaire'),
        ('VETERINAIRE', 'Frais vétérinaires'),
        ('LOCATION', 'Location'),
        ('TRANSPORT', 'Transport'),
        ('AUTRE_DEPENSE', 'Autre dépense'),
        ('VENTE_ANIMAUX', 'Vente d\'animaux'),
        ('VENTE_OEUFS', 'Vente d\'œufs'),
        ('VENTE_CULTURES', 'Vente de récoltes'),
        ('AUTRE_RECETTE', 'Autre recette'),
    ]

    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=date.today)
    commentaire = models.TextField(blank=True)
    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def clean(self):
        super().clean()
        if self.montant is not None and self.montant <= 0:
            raise ValidationError("Le montant doit être strictement positif.")
        if self.date and self.date > date.today():
            raise ValidationError("La date ne peut pas être dans le futur.")
        if self.type == 'DEPENSE' and self.categorie not in self.CATEGORIES_DEPENSE:
            raise ValidationError("Cette catégorie n'est pas valide pour une dépense.")
        if self.type == 'RECETTE' and self.categorie not in self.CATEGORIES_RECETTE:
            raise ValidationError("Cette catégorie n'est pas valide pour une recette.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} — {self.get_categorie_display()} — {self.montant} FCFA ({self.date})"