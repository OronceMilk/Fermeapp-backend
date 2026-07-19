import pytest
from datetime import date, timedelta
from accounts.models import Ferme, User
from cheptel.models import Espece, LotPondeuses, Animal, Produit

# -------- FIXTURES TRANSVERSALES (partagées entre toutes les apps) --------

@pytest.fixture
def ferme():
    return Ferme.objects.create(
        nom="Ferme Test",
        localisation="Tori-Bossito",
        email="ferme-test@example.com",
    )

@pytest.fixture
def ferme_autre():
    return Ferme.objects.create(
        nom="Ferme Autre",
        localisation="Allada",
        email="ferme-autre@example.com",
    )

@pytest.fixture
def admin_user(ferme):
    return User.objects.create_user(
        username="admin_test",
        email="admin@test.com",
        password="TestPass123!",
        ferme=ferme,
        role="ADMIN",
    )

# -------- FIXTURES CHEPTEL (partagées pour dashboard/services) --------

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