import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cheptel.models import RapportJournalier

pytestmark = pytest.mark.django_db

def test_valeurs_negatives_refusees(ferme, admin_user):
    with pytest.raises(ValidationError):
        RapportJournalier.objects.create(
            ferme=ferme, date=date.today(), nombre_morts=-1, createur=admin_user,
        )

def test_date_future_refusee(ferme, admin_user):
    with pytest.raises(ValidationError):
        RapportJournalier.objects.create(
            ferme=ferme, date=date.today() + timedelta(days=1), createur=admin_user,
        )

def test_doublon_ferme_date_refuse(ferme, admin_user):
    RapportJournalier.objects.create(ferme=ferme, date=date.today(), createur=admin_user)
    with pytest.raises(ValidationError):
        RapportJournalier.objects.create(ferme=ferme, date=date.today(), createur=admin_user)