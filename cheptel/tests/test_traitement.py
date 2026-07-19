import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cheptel.models import Traitement

pytestmark = pytest.mark.django_db

def test_traitement_futur_refuse(ferme, animal, produit, admin_user):
    with pytest.raises(ValidationError):
        Traitement.objects.create(
            animal=animal, ferme=ferme, type="VACCIN",
            date=date.today() + timedelta(days=1),
            produit=produit, operateur=admin_user,
        )

def test_traitement_animal_decede_refuse(ferme, animal, produit, admin_user):
    animal.statut = "DECEDE"
    animal.save()
    with pytest.raises(ValidationError):
        Traitement.objects.create(
            animal=animal, ferme=ferme, type="TRAITEMENT",
            date=date.today(), produit=produit, operateur=admin_user,
        )

def test_rappel_avant_date_traitement_refuse(ferme, animal, produit, admin_user):
    with pytest.raises(ValidationError):
        Traitement.objects.create(
            animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
            rappel_le=date.today() - timedelta(days=1),
            produit=produit, operateur=admin_user,
        )

def test_traitement_valide_avec_rappel_futur_accepte(ferme, animal, produit, admin_user):
    traitement = Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=30),
        produit=produit, operateur=admin_user,
    )
    assert traitement.pk is not None