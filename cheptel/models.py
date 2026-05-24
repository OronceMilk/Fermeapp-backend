from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User


# ==============================
# ESPÈCE
# ==============================
class Espece(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Espèce"
        verbose_name_plural = "Espèces"
        indexes = [
            models.Index(fields=['nom']),
        ]

    def __str__(self):
        return self.nom


# ==============================
# PRODUIT
# ==============================
class Produit(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        indexes = [
            models.Index(fields=['nom']),
        ]

    def __str__(self):
        return self.nom


# ==============================
# LOT DE PONDEUSES (MODIFIÉ)
# ==============================
class LotPondeuses(models.Model):
    nom = models.CharField(max_length=100)

    # 🔥 NOUVEAU : Lien vers la ferme
    ferme = models.ForeignKey(
        'accounts.Ferme',
        on_delete=models.CASCADE,
        related_name='lots'
    )

    espece = models.ForeignKey(
        Espece,
        on_delete=models.PROTECT,
        related_name='lots'
    )

    nombre_sujets = models.PositiveIntegerField()
    date_mise_en_place = models.DateField()

    race = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    createur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lots_crees'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lot de pondeuses"
        verbose_name_plural = "Lots de pondeuses"
        indexes = [
            models.Index(fields=['espece']),
            models.Index(fields=['ferme']),  # 🔥 Index pour performance
        ]

    def __str__(self):
        return f"{self.nom} ({self.nombre_sujets} sujets)"


# ==============================
# ANIMAL
# ==============================
class Animal(models.Model):
    STATUTS = [
        ('ACTIF', 'Actif'),
        ('VENDU', 'Vendu'),
        ('DECEDE', 'Décédé'),
    ]

    SEXES = [
        ('M', 'Mâle'),
        ('F', 'Femelle'),
    ]

    identifiant = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100, blank=True)

    # Lien vers la ferme (indispensable pour multi-ferme)
    ferme = models.ForeignKey(
        'accounts.Ferme',
        on_delete=models.CASCADE,
        related_name='animaux'
    )

    espece = models.ForeignKey(
        Espece,
        on_delete=models.PROTECT,
        related_name='animaux'
    )

    lot = models.ForeignKey(
        LotPondeuses,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animaux'
    )

    race = models.CharField(max_length=100, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXES)

    date_naissance = models.DateField(null=True, blank=True)
    date_arrivee = models.DateField(auto_now_add=True)

    statut = models.CharField(max_length=10, choices=STATUTS, default='ACTIF')

    photo = models.FileField(upload_to='animaux/', null=True, blank=True)

    notes = models.TextField(blank=True)

    createur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animaux_crees'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animaux"
        ordering = ['-date_arrivee']
        indexes = [
            models.Index(fields=['identifiant']),
            models.Index(fields=['statut']),
            models.Index(fields=['espece']),
            models.Index(fields=['ferme']),
        ]

    def clean(self):
        super().clean()

        if self.date_naissance and self.date_arrivee:
            if self.date_naissance > self.date_arrivee:
                raise ValidationError("La date de naissance ne peut pas être après la date d'arrivée.")

        if self.lot and self.lot.espece != self.espece:
            raise ValidationError("L'espèce de l'animal doit correspondre au lot.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.identifiant} - {self.nom or self.espece.nom}"


# ==============================
# TRAITEMENT SANITAIRE (MODIFIÉ)
# ==============================
class Traitement(models.Model):
    TYPES = [
        ('VACCIN', 'Vaccination'),
        ('TRAITEMENT', 'Traitement'),
        ('MALADIE', 'Maladie'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='traitements'
    )

    # 🔥 NOUVEAU : Lien vers la ferme
    ferme = models.ForeignKey(
        'accounts.Ferme',
        on_delete=models.CASCADE,
        related_name='traitements'
    )

    type = models.CharField(max_length=20, choices=TYPES)
    date = models.DateField()

    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        related_name='traitements'
    )

    dose = models.CharField(max_length=100, blank=True)

    rappel_le = models.DateField(null=True, blank=True)

    operateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='traitements_effectues'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Traitement"
        verbose_name_plural = "Traitements"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['ferme']),  # 🔥 Index pour performance
        ]

    def clean(self):
        super().clean()

        if self.date > timezone.now().date():
            raise ValidationError("La date du traitement ne peut pas être dans le futur.")

        if self.animal and self.animal.statut == 'DECEDE':
            raise ValidationError("Impossible de traiter un animal décédé.")

        if self.rappel_le and self.rappel_le <= self.date:
            raise ValidationError("La date de rappel doit être postérieure à la date du traitement.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal} - {self.get_type_display()} ({self.date})"


# ==============================
# COMPTAGE DES ŒUFS
# ==============================
class ComptageOeufs(models.Model):
    lot = models.ForeignKey(
        LotPondeuses,
        on_delete=models.CASCADE,
        related_name='comptages'
    )

    date = models.DateField()
    nombre = models.PositiveIntegerField()

    createur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comptages_crees'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comptage d'œufs"
        verbose_name_plural = "Comptages d'œufs"
        constraints = [
            models.UniqueConstraint(fields=['lot', 'date'], name='unique_lot_date')
        ]
        indexes = [
            models.Index(fields=['date']),
        ]

    def clean(self):
        super().clean()

        if self.nombre < 0:
            raise ValidationError("Le nombre d'œufs ne peut pas être négatif.")

        if self.date > timezone.now().date():
            raise ValidationError("La date ne peut pas être dans le futur.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lot} - {self.date} : {self.nombre} œufs"


# ==============================
# RAPPORT JOURNALIER
# ==============================
class RapportJournalier(models.Model):
    ferme = models.ForeignKey(
        'accounts.Ferme',
        on_delete=models.CASCADE,
        related_name='rapports'
    )

    date = models.DateField()

    # Données quotidiennes
    nombre_morts = models.PositiveIntegerField(default=0, help_text="Nombre d'animaux morts aujourd'hui")
    oeufs_pondus = models.PositiveIntegerField(default=0, help_text="Nombre d'œufs pondus aujourd'hui")
    aliment_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Aliments consommés (kg)")
    eau_litres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Eau servie (litres)")
    sujets_malades = models.PositiveIntegerField(default=0, help_text="Nombre d'animaux malades")

    notes = models.TextField(blank=True)

    # Traçabilité
    createur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rapports_crees'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rapport journalier"
        verbose_name_plural = "Rapports journaliers"
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['ferme', 'date'], name='unique_rapport_ferme_date')
        ]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['ferme', 'date']),
        ]

    def clean(self):
        super().clean()

        if self.date > timezone.now().date():
            raise ValidationError("La date ne peut pas être dans le futur.")

        if self.nombre_morts < 0 or self.oeufs_pondus < 0 or self.sujets_malades < 0:
            raise ValidationError("Les valeurs numériques ne peuvent pas être négatives.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rapport du {self.date} - {self.ferme.nom}"
