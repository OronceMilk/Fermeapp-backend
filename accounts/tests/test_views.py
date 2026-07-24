import pytest
from django.test import Client
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_username_avec_espace_erreur_propre():
    client = Client()
    response = client.post(reverse('accounts:inscription'), {
        'ferme_nom': 'Ferme Test',
        'ferme_localisation': 'Tori-Bossito',
        'ferme_email': 'ferme@test.com',
        'admin_username': 'BArry Wallas',  # contient un espace
        'admin_email': 'admin@test.com',
        'admin_password': 'TestPass123!',
        'admin_password_confirm': 'TestPass123!',
    })
    assert response.status_code == 200
    # Vérifie qu'un message d'erreur est affiché (pas de crash 500)
    content = response.content.decode('utf-8')
    assert 'espace' in content.lower() or 'invalide' in content.lower()
