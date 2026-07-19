import pytest
from dashboard.services.kpi_service import get_kpis
from cheptel.models import Animal

pytestmark = pytest.mark.django_db

def test_kpis_isoles_par_ferme(ferme, ferme_autre, espece, admin_user):
    Animal.objects.create(identifiant="A1", ferme=ferme, espece=espece, sexe="F")
    Animal.objects.create(identifiant="A2", ferme=ferme_autre, espece=espece, sexe="M")

    kpis = get_kpis(admin_user)  # admin_user appartient à `ferme`

    assert kpis['total_animaux'] == 1  # pas 2 — preuve de l'isolation multi-ferme