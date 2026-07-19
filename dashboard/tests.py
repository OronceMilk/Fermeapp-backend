import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import User

pytestmark = pytest.mark.django_db

def test_dashboard_utilisateur_sans_ferme_pas_de_crash(ferme):
    user_sans_ferme = User.objects.create_superuser(
        username="super_sans_ferme",
        email="super@test.com",
        password="TestPass123!",
    )
    client = Client()
    client.force_login(user_sans_ferme)
    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    assert response.context.get("no_ferme") is True