import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cultures.models import CultureParcelle

pytestmark = pytest.mark.django_db

def test_creation_orm_directe_ne_valide_pas_automatiquement(parcelle, culture):
    """
    ⚠️ Ce test documente un comportement réel, pas un comportement souhaité.
    CultureParcelle n'appelle pas full_clean() dans save().
    """
    cp = CultureParcelle.objects.create(
        parcelle=parcelle, culture=culture,
        date_semis=date.today(),
        date_recolte_prevue=date.today() - timedelta(days=5),
    )
    assert cp.pk is not None

def test_full_clean_explicite_detecte_bien_incoherence(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today(),
        date_recolte_prevue=date.today() - timedelta(days=5),
    )
    with pytest.raises(ValidationError):
        cp.full_clean()

def test_recolte_reelle_avant_semis_detectee_par_full_clean(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today(),
        date_recolte_reelle=date.today() - timedelta(days=1),
    )
    with pytest.raises(ValidationError):
        cp.full_clean()

def test_dates_coherentes_acceptees(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today() - timedelta(days=60),
        date_recolte_prevue=date.today() + timedelta(days=30),
    )
    cp.full_clean()