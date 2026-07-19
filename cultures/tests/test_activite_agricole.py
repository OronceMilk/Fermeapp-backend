import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cultures.models import ActiviteAgricole

pytestmark = pytest.mark.django_db

def test_date_future_detectee_par_full_clean(culture_parcelle):
    activite = ActiviteAgricole(
        culture_parcelle=culture_parcelle, type="IRRIGATION",
        date=date.today() + timedelta(days=1),
    )
    with pytest.raises(ValidationError):
        activite.full_clean()

def test_creation_orm_directe_ne_valide_pas_automatiquement(culture_parcelle):
    activite = ActiviteAgricole.objects.create(
        culture_parcelle=culture_parcelle, type="LABOUR",
        date=date.today() + timedelta(days=1),
    )
    assert activite.pk is not None