import pytest
from decimal import Decimal
from dashboard.services.finance_service import get_finances
from stocks.models import ProduitStock, MouvementStock
from django.db.models.functions import TruncMonth

pytestmark = pytest.mark.django_db


def test_get_finances_agrege_stock_et_transactions_hors_stock(ferme, admin_user):
    """
    P15 : remplace l'ancien test qui documentait l'estimation à 1.3x (retirée).
    Vérifie que depenses = MouvementStock (stock) + Transaction (hors-stock),
    et que recettes proviennent uniquement de Transaction — plus d'estimation.
    """
    from finances.models import Transaction

    produit = ProduitStock.objects.create(
        ferme=ferme, nom="Aliment volaille", unite="KG",
        prix_moyen_unitaire=Decimal('500'),
    )
    MouvementStock.objects.create(
        produit=produit, type='ENTREE', quantite=10,
        prix_unitaire=Decimal('500'), created_by=admin_user,
    )  # dépense stock = 5000

    Transaction.objects.create(
        ferme=ferme, type='DEPENSE', categorie='SALAIRE',
        montant=Decimal('20000'), createur=admin_user,
    )  # dépense hors-stock = 20000

    Transaction.objects.create(
        ferme=ferme, type='RECETTE', categorie='VENTE_OEUFS',
        montant=Decimal('80000'), createur=admin_user,
    )

    finances = get_finances(admin_user)
    assert finances['depenses'] == 25000.0    # 5000 + 20000
    assert finances['recettes'] == 80000.0    # réel, plus d'estimation
    assert finances['marge'] == 55000.0


def test_get_finances_sans_transaction_ni_mouvement_tout_a_zero(ferme, admin_user):
    """Cas limite : ferme neuve, cohérent avec le dashboard vide de P14."""
    finances = get_finances(admin_user)
    assert finances == {'recettes': 0.0, 'depenses': 0.0, 'marge': 0.0}
