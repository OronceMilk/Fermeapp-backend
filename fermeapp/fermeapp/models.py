from django.db import models
from django.contrib.auth.models import User


class Animal(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('malade', 'Malade'),
        ('reproduction', 'En reproduction'),
        ('vente', 'À vendre'),
    ]

    ESPECE_CHOICES = [
        ('vache', 'Vache'),
        ('taureau', 'Taureau'),
        ('veau', 'Veau'),
        ('brebis', 'Brebis'),
        ('belier', 'Bélier'),
        ('agneau', 'Agneau'),
    ]

    SEXE_CHOICES = [
        ('M', 'Mâle'),
        ('F', 'Femelle'),
    ]

    nom = models.CharField(max_length=100)
    numero_identification = models.CharField(max_length=50, unique=True)
    espece = models.CharField(max_length=20, choices=ESPECE_CHOICES)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField(null=True, blank=True)
    lot = models.CharField(max_length=50, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    photo = models.FileField(upload_to='animals/', null=True, blank=True)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.numero_identification})"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animaux"


class Traitement(models.Model):
    TYPE_CHOICES = [
        ('vaccin', 'Vaccin'),
        ('medicament', 'Médicament'),
        ('vermifuge', 'Vermifuge'),
        ('soins', 'Soins'),
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='traitements')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    date = models.DateField()
    date_prochaine = models.DateField(null=True, blank=True)
    veterinaire = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.animal.nom} ({self.date})"

    class Meta:
        verbose_name = "Traitement"
        verbose_name_plural = "Traitements"
        ordering = ['-date']