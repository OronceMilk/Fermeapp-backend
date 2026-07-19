import pytest
from datetime import date, timedelta
from cheptel.models import Espece, LotPondeuses, Animal, Produit

@pytest.fixture
def espece():
    return Espece.objects.create(nom="Poule pondeuse")

@pytest.fixture
def espece_autre():
    return Espece.objects.create(nom="Chèvre")

@pytest.fixture
def lot(ferme, espece):
    return LotPondeuses.objects.create(
        nom="Lot A", ferme=ferme, espece=espece,
        nombre_sujets=50, date_mise_en_place=date.today() - timedelta(days=30),
    )

@pytest.fixture
def animal(ferme, espece, admin_user):
    return Animal.objects.create(
        identifiant="AN-001", ferme=ferme, espece=espece,
        sexe="F", createur=admin_user,
    )

@pytest.fixture
def produit():
    return Produit.objects.create(nom="Vaccin Newcastle")