# stocks/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User, Ferme


class ProduitStock(models.Model):
    """Fiche produit pour la gestion des stocks d'intrants"""
    
    UNITE_CHOICES = [
        ('KG', 'Kilogramme (kg)'),
        ('L', 'Litre (L)'),
        ('SAC', 'Sac (50kg)'),
        ('BONBONNE', 'Bonne (20L)'),
        ('UNITE', 'Pièce unitaire'),
    ]
    
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='stocks')
    
    nom = models.CharField(max_length=100)
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES, default='KG')
    emplacement = models.CharField(max_length=100, blank=True)
    
    # 🔥 DecimalField au lieu de FloatField
    quantite_actuelle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_alerte = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    fournisseur_principal = models.CharField(max_length=100, blank=True)
    prix_moyen_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produit de stock"
        verbose_name_plural = "Stocks"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['ferme']),
            models.Index(fields=['seuil_alerte']),
            models.Index(fields=['quantite_actuelle']),
        ]
        unique_together = [['ferme', 'nom']]
    
    def est_en_alerte(self):
        return self.quantite_actuelle <= self.seuil_alerte
    
    def __str__(self):
        return f"{self.nom} ({self.quantite_actuelle} {self.get_unite_display()})"


class MouvementStock(models.Model):
    """Cœur du module - Source de vérité"""
    
    TYPE_CHOICES = [
        ('ENTREE', '📥 Entrée (achat, production)'),
        ('SORTIE', '📤 Sortie (consommation, vente)'),
    ]
    
    produit = models.ForeignKey(
        ProduitStock, 
        on_delete=models.PROTECT,
        related_name='mouvements'
    )
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    
    motif = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    
    # 🔥 Pour dashboard financier
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 🔥 Traçabilité complète
    stock_avant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_apres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mouvements_stock')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['produit']),
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['produit', 'date']),
        ]
    
    def clean(self):
        super().clean()
        
        if self.quantite is not None and self.quantite <= 0:
            raise ValidationError("La quantité doit être strictement positive.")
        
        if self.date and self.date > timezone.now().date():
            raise ValidationError("La date ne peut pas être dans le futur.")
        
        if self.prix_unitaire and self.prix_unitaire <= 0:
            raise ValidationError("Le prix unitaire doit être positif.")
    
    def __str__(self):
        direction = "+" if self.type == 'ENTREE' else "-"
        return f"{self.produit.nom}: {direction}{self.quantite} ({self.date})"