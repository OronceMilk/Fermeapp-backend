import pytest
from django.urls import reverse
from django.test import Client
from finances.models import Transaction

pytestmark = pytest.mark.django_db


def test_liste_transactions_isolee_par_ferme(ferme, ferme_autre, admin_user):
    Transaction.objects.create(ferme=ferme, type='DEPENSE', categorie='SALAIRE', montant=1000, createur=admin_user)
    Transaction.objects.create(ferme=ferme_autre, type='DEPENSE', categorie='SALAIRE', montant=2000)

    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse('finances:liste'))

    assert response.status_code == 200
    assert len(response.context['transactions']) == 1


def test_creation_transaction_pas_de_double_enregistrement(ferme, admin_user):
    client = Client()
    client.force_login(admin_user)
    client.post(reverse('finances:creer'), {
        'type': 'RECETTE', 'categorie': 'VENTE_OEUFS',
        'montant': '50000', 'date': '2026-07-01', 'commentaire': 'Test',
    })
    assert Transaction.objects.filter(categorie='VENTE_OEUFS').count() == 1