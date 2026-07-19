import pytest
from datetime import date
from cultures.models import Parcelle, Culture, CultureParcelle

@pytest.fixture
def parcelle(ferme):
    return Parcelle.objects.create(
        nom="Parcelle Nord", superficie=2.5, ferme=ferme,
    )

@pytest.fixture
def culture():
    return Culture.objects.create(nom="Maïs")

@pytest.fixture
def culture_parcelle(parcelle, culture):
    return CultureParcelle.objects.create(
        parcelle=parcelle, culture=culture, date_semis=date.today(),
    )