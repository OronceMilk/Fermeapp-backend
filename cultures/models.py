# cultures/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User, Ferme


class Parcelle(models.Model):
    """Représente une parcelle de terre dans la ferme"""
    nom = models.CharField(max_length=100)
    superficie = models.DecimalField(max_digits=6, decimal_places=2, help_text="Superficie en hectares")
    type_sol = models.CharField(max_length=100, blank=True, help_text="Type de sol (argileux, sableux, etc.)")
    localisation = models.CharField(max_length=255, blank=True, help_text="Description de l'emplacement")
    
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='parcelles')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Parcelle"
        verbose_name_plural = "Parcelles"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['ferme']),
            models.Index(fields=['nom']),
        ]
        unique_together = [['ferme', 'nom']]  # Une ferme ne peut pas avoir deux parcelles avec le même nom
    
    def __str__(self):
        return f"{self.nom} ({self.superficie} ha)"


class Culture(models.Model):
    """Liste des cultures possibles (maïs, soja, riz, etc.)"""
    nom = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Culture"
        verbose_name_plural = "Cultures"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['nom']),
        ]
    
    def __str__(self):
        return self.nom


class CultureParcelle(models.Model):
    """Relation entre une culture et une parcelle avec les dates de culture"""
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='cultures_associees')
    culture = models.ForeignKey(Culture, on_delete=models.PROTECT, related_name='parcelles_associees')
    
    date_semis = models.DateField()
    date_recolte_prevue = models.DateField(null=True, blank=True)
    date_recolte_reelle = models.DateField(null=True, blank=True)
    
    rendement = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Production en kg"
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Culture sur parcelle"
        verbose_name_plural = "Cultures sur parcelles"
        ordering = ['-date_semis']
        indexes = [
            models.Index(fields=['parcelle']),
            models.Index(fields=['culture']),
            models.Index(fields=['date_semis']),
        ]
        unique_together = [['parcelle', 'date_semis']]  # Une parcelle ne peut avoir qu'un semis par date
    
    def clean(self):
        super().clean()
        
        if self.date_recolte_prevue and self.date_recolte_prevue < self.date_semis:
            raise ValidationError("La date de récolte prévue doit être après la date de semis.")
        
        if self.date_recolte_reelle and self.date_recolte_reelle < self.date_semis:
            raise ValidationError("La date de récolte réelle doit être après la date de semis.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.culture.nom} - {self.parcelle.nom} (semis: {self.date_semis})"


class ActiviteAgricole(models.Model):
    """Activités réalisées sur une culture (labour, irrigation, fertilisation, etc.)"""
    TYPES = [
        ('LABOUR', 'Labour'),
        ('SEMIS', 'Semis'),
        ('IRRIGATION', 'Irrigation'),
        ('FERTILISATION', 'Fertilisation'),
        ('DESHERBAGE', 'Désherbage'),
        ('TRAITEMENT', 'Traitement phytosanitaire'),
        ('RECOLTE', 'Récolte'),
    ]
    
    culture_parcelle = models.ForeignKey(
        CultureParcelle, on_delete=models.CASCADE,
        related_name='activites'
    )
    
    type = models.CharField(max_length=20, choices=TYPES)
    date = models.DateField()
    
    description = models.TextField(blank=True)
    intrants_utilises = models.CharField(max_length=255, blank=True, help_text="Engrais, pesticides, etc.")
    
    operateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='activites_agricoles'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Activité agricole"
        verbose_name_plural = "Activités agricoles"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['culture_parcelle']),
        ]
    
    def clean(self):
        super().clean()
        
        if self.date > timezone.now().date():
            raise ValidationError("La date ne peut pas être dans le futur.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.culture_parcelle} - {self.date}"