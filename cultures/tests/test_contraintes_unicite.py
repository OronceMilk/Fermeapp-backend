import pytest
from datetime import date
from django.db import IntegrityError, transaction
from cultures.models import Parcelle, CultureParcelle

pytestmark = pytest.mark.django_db

def test_deux_parcelles_meme_nom_meme_ferme_refuse(ferme):
    Parcelle.objects.create(nom="Parcelle A", superficie=1.0, ferme=ferme)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Parcelle.objects.create(nom="Parcelle A", superficie=2.0, ferme=ferme)

def test_meme_nom_parcelle_fermes_differentes_accepte(ferme, ferme_autre):
    Parcelle.objects.create(nom="Parcelle A", superficie=1.0, ferme=ferme)
    p2 = Parcelle.objects.create(nom="Parcelle A", superficie=1.5, ferme=ferme_autre)
    assert p2.pk is not None

def test_deux_semis_meme_parcelle_meme_date_refuse(parcelle, culture):
    from django.core.exceptions import ValidationError

    CultureParcelle.objects.create(parcelle=parcelle, culture=culture, date_semis=date.today())
    with pytest.raises(ValidationError):
        CultureParcelle.objects.create(parcelle=parcelle, culture=culture, date_semis=date.today())