# accounts/services.py
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from accounts.models import Ferme, User


class EmailDejaUtiliseException(Exception):
    """Exception levée lorsque l'email de la ferme ou de l'utilisateur est déjà utilisé."""
    pass


@transaction.atomic
def inscrire_nouvelle_ferme(donnees_ferme, donnees_admin):
    """
    Crée une nouvelle ferme et son administrateur principal dans une transaction atomique.
    
    Args:
        donnees_ferme (dict): {
            'nom': str,
            'localisation': str,
            'email': str,
            'telephone': str (optionnel)
        }
        donnees_admin (dict): {
            'username': str,
            'email': str,
            'password': str (non hashé),
            'role': 'ADMIN'  # forcé
        }
    
    Returns:
        User: L'utilisateur admin créé, lié à la nouvelle ferme.
    
    Raises:
        EmailDejaUtiliseException: Si l'email de la ferme ou de l'utilisateur existe déjà.
        ValidationError: Si les données ne sont pas valides (passé par les modèles).
    """
    # Vérifier que l'email de la ferme n'est pas déjà utilisé
    if Ferme.objects.filter(email=donnees_ferme['email']).exists():
        raise EmailDejaUtiliseException("Cette adresse email est déjà utilisée par une autre ferme.")
    
    # Créer la ferme
    ferme = Ferme.objects.create(
        nom=donnees_ferme['nom'],
        localisation=donnees_ferme['localisation'],
        email=donnees_ferme['email'],
        telephone=donnees_ferme.get('telephone', ''),
    )
    
    # Toute erreur lors de la création de l'admin doit annuler aussi la ferme.
    try:
        user = User.objects.create_user(
            username=donnees_admin['username'],
            email=donnees_admin['email'],
            password=donnees_admin['password'],
            role='ADMIN',
            ferme=ferme,
        )
    except (IntegrityError, ValidationError) as exc:
        raise EmailDejaUtiliseException(
            "Cette adresse email est déjà utilisée par un autre compte."
        ) from exc
    
    return user