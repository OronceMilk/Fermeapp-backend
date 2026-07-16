from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy


# ==============================
# FERME
# ==============================
class Ferme(models.Model):
    nom = models.CharField(max_length=255)
    localisation = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ferme"
        verbose_name_plural = "Fermes"

    def __str__(self):
        return self.nom

    # ==============================
    # 🔥 PROPRIÉTÉS AJOUTÉES
    # ==============================
    @property
    def admin_principal(self):
        """Retourne l'administrateur principal de la ferme"""
        return self.utilisateurs.filter(role='ADMIN').first()

    @property
    def a_un_admin(self):
        """Vérifie si la ferme a un administrateur"""
        return self.utilisateurs.filter(role='ADMIN').exists()


# ==============================
# UTILISATEUR
# ==============================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('EMPLOYE', 'Employé'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYE')

    phone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=255, blank=True)

    # 🔥 Lien vers la ferme
    ferme = models.ForeignKey(
        Ferme,
        on_delete=models.CASCADE,
        related_name='utilisateurs',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        # 🔥 PERMISSIONS AJOUTÉES CI-DESSOUS
        permissions = [
            ("can_manage_users", "Peut gérer les utilisateurs de sa ferme"),
            ("can_view_reports", "Peut consulter tous les rapports"),
            ("can_export_data", "Peut exporter les données"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # ==============================
    # VALIDATION MÉTIER 🔥
    # ==============================
    def clean(self):
        super().clean()

        # � P0.4 : Les superusers sont des comptes plateforme, pas des comptes métier
        if not self.ferme and not self.is_superuser:
            raise ValidationError("Un utilisateur doit être rattaché à une ferme.")

        # 🔴 Un seul ADMIN par ferme
        if self.role == 'ADMIN':
            qs = User.objects.filter(ferme=self.ferme, role='ADMIN')

            # Exclure lui-même en modification
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError("Cette ferme possède déjà un administrateur.")

    # ==============================
    # SAUVEGARDE SÉCURISÉE 🔐
    # ==============================
    def save(self, *args, **kwargs):
        self.full_clean()  # force validation avant sauvegarde
        super().save(*args, **kwargs)

    # ==============================
    # REDIRECTION INTELLIGENTE 🧭
    # ==============================
    def get_dashboard_url(self):
        """Retourne l'URL du dashboard selon le rôle"""
        if self.role == 'ADMIN':
            return reverse_lazy('accounts:admin_dashboard')
        elif self.role == 'EMPLOYE':
            return reverse_lazy('accounts:employe_dashboard')
        else:
            return reverse_lazy('admin:index')