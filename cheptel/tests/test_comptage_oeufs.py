import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from cheptel.models import ComptageOeufs

pytestmark = pytest.mark.django_db

def test_nombre_negatif_refuse(lot, admin_user):
    with pytest.raises(ValidationError):
        ComptageOeufs.objects.create(lot=lot, date=date.today(), nombre=-5, createur=admin_user)

def test_date_future_refusee(lot, admin_user):
    with pytest.raises(ValidationError):
        ComptageOeufs.objects.create(
            lot=lot, date=date.today() + timedelta(days=1), nombre=10, createur=admin_user,
        )

def test_doublon_lot_date_refuse(lot, admin_user):
    ComptageOeufs.objects.create(lot=lot, date=date.today(), nombre=10, createur=admin_user)
    with pytest.raises(ValidationError):
        ComptageOeufs.objects.create(lot=lot, date=date.today(), nombre=15, createur=admin_user)