import pytest
from decimal import Decimal
from finances.services import creer_transaction, get_transactions_ferme, get_total_par_type
from finances.models import Transaction

pytestmark = pytest.mark.django_db


def test_creer_transaction(ferme, admin_user):
    t = creer_transaction(
        ferme=ferme, createur=admin_user, type='RECETTE',
        categorie='VENTE_OEUFS', montant=Decimal('50000'),
    )
    assert t.pk is not None


def test_get_transactions_ferme_isole_par_ferme(ferme, ferme_autre):
    Transaction.objects.create(ferme=ferme, type='DEPENSE', categorie='SALAIRE', montant=1000)
    Transaction.objects.create(ferme=ferme_autre, type='DEPENSE', categorie='SALAIRE', montant=2000)
    assert get_transactions_ferme(ferme).count() == 1


def test_get_total_par_type_filtre_par_mois(ferme):
    from datetime import date
    Transaction.objects.create(ferme=ferme, type='RECETTE', categorie='VENTE_OEUFS', montant=1000, date=date(2026, 3, 1))
    Transaction.objects.create(ferme=ferme, type='RECETTE', categorie='VENTE_OEUFS', montant=2000, date=date(2026, 4, 1))

    total_mars = get_total_par_type(ferme, 'RECETTE', annee=2026, mois=3)
    assert total_mars == Decimal('1000')