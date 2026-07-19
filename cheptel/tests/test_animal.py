import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cheptel.models import Animal, LotPondeuses

pytestmark = pytest.mark.django_db

def test_animal_creation_valide(ferme, espece, admin_user):
    animal = Animal.objects.create(
        identifiant="AN-100", ferme=ferme, espece=espece,
        sexe="M", createur=admin_user,
    )
    assert animal.pk is not None
    assert animal.statut == "ACTIF"

def test_naissance_apres_arrivee_refusee(ferme, espece, admin_user):
    with pytest.raises(ValidationError):
        Animal.objects.create(
            identifiant="AN-101", ferme=ferme, espece=espece, sexe="F",
            date_naissance=date.today() + timedelta(days=1),
            date_arrivee=date.today(),
            createur=admin_user,
        )

def test_espece_incoherente_avec_lot_refusee(ferme, espece, espece_autre, admin_user):
    lot = LotPondeuses.objects.create(
        nom="Lot poules", ferme=ferme, espece=espece,
        nombre_sujets=10, date_mise_en_place=date.today(),
    )
    with pytest.raises(ValidationError):
        Animal.objects.create(
            identifiant="AN-102", ferme=ferme, espece=espece_autre,
            lot=lot, sexe="F", createur=admin_user,
        )

def test_espece_coherente_avec_lot_acceptee(ferme, espece, admin_user):
    lot = LotPondeuses.objects.create(
        nom="Lot poules", ferme=ferme, espece=espece,
        nombre_sujets=10, date_mise_en_place=date.today(),
    )
    animal = Animal.objects.create(
        identifiant="AN-103", ferme=ferme, espece=espece,
        lot=lot, sexe="F", createur=admin_user,
    )
    assert animal.lot == lot