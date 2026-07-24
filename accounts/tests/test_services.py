import pytest
from django.core.exceptions import ValidationError
from accounts.models import Ferme, User
from accounts.services import inscrire_nouvelle_ferme, EmailDejaUtiliseException
from django.db import IntegrityError


pytestmark = pytest.mark.django_db

def test_inscription_reussie():
    user = inscrire_nouvelle_ferme(  
        donnees_ferme={
            'nom': 'Ferme Test',
            'localisation': 'Tori-Bossito',
            'email': 'ferme@test.com',
            'telephone': '+22997000000',
        },
        donnees_admin={
            'username': 'admin_test',
            'email': 'admin@test.com',
            'password': 'TestPass123!',
        }
    )
    assert user.pk is not None
    assert user.role == 'ADMIN'
    assert user.ferme is not None
    assert Ferme.objects.filter(email='ferme@test.com').exists()

def test_email_ferme_deja_utilise(ferme):
    with pytest.raises(EmailDejaUtiliseException):
        inscrire_nouvelle_ferme(
            donnees_ferme={
                'nom': 'Ferme Doublon',
                'localisation': 'Cotonou',
                'email': ferme.email,  # email déjà utilisé
            },
            donnees_admin={
                'username': 'admin_doublon',
                'email': 'admin@test.com',
                'password': 'TestPass123!',
            }
        )

def test_email_admin_deja_utilise(admin_user):
    with pytest.raises(EmailDejaUtiliseException):
        inscrire_nouvelle_ferme(
            donnees_ferme={
                'nom': 'Ferme Test 2',
                'localisation': 'Allada',
                'email': 'ferme2@test.com',
            },
            donnees_admin={
                'username': 'admin_doublon2',
                'email': admin_user.email,  # email déjà utilisé
                'password': 'TestPass123!',
            }
        )

def test_rollback_si_validation_echoue():
    """
    Vérifie qu'aucune ferme n'est créée si une exception est levée après la création de la ferme.
    On simule une violation de la contrainte d'unicité sur l'email de l'utilisateur,
    en utilisant l'email déjà présent dans la base (admin@example.com).
    """
    ferme_existante = Ferme.objects.create(
        nom='Ferme Existante',
        localisation='Cotonou',
        email='existante@test.com',
    )
    User.objects.create_user(
        username='admin_existant',
        email='admin@example.com',
        password='TestPass123!',
        role='ADMIN',
        ferme=ferme_existante,
    )
    ferme_count_avant = Ferme.objects.count()
    
    with pytest.raises(EmailDejaUtiliseException):
        inscrire_nouvelle_ferme(
            donnees_ferme={
                'nom': 'Ferme Test Rollback',
                'localisation': 'Parakou',
                'email': 'rollback_ferme@test.com',
            },
            donnees_admin={
                'username': 'admin_rollback',
                'email': 'admin@example.com',  # email déjà utilisé par l'utilisateur existant
                'password': 'TestPass123!',
            }
        )
    
    # La ferme ne doit pas être créée (rollback)
    assert Ferme.objects.filter(email='rollback_ferme@test.com').count() == 0