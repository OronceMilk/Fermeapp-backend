import pytest
from django.test import Client
from django.urls import reverse
from stocks.models import ProduitStock

pytestmark = pytest.mark.django_db

def test_utilisateur_ne_voit_pas_produits_autre_ferme(ferme, ferme_autre, admin_user):
    ProduitStock.objects.create(ferme=ferme_autre, nom="Produit isolé", unite="KG")

    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse("stocks:dashboard"))

    assert response.status_code == 200
    noms_visibles = [p.nom for p in response.context.get("produits", [])]
    assert "Produit isolé" not in noms_visibles