import pytest
from django.test import Client
from django.urls import reverse
from cultures.models import Parcelle

pytestmark = pytest.mark.django_db

def test_utilisateur_ne_voit_pas_parcelles_autre_ferme(ferme, ferme_autre, admin_user):
    Parcelle.objects.create(ferme=ferme_autre, nom="Parcelle isolée", superficie=1.0)

    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse("cultures:parcelle_list"))

    assert response.status_code == 200
    noms_visibles = [p.nom for p in response.context.get("parcelles", [])]
    assert "Parcelle isolée" not in noms_visibles