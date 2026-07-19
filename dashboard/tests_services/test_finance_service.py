import pytest
from decimal import Decimal
from datetime import date
from dashboard.services.finance_service import get_finances
from stocks.models import ProduitStock, MouvementStock

pytestmark = pytest.mark.django_db

def test_marge_calculee_a_30_pourcent(ferme, admin_user):
    """
    ⚠️ Ce test documente une estimation MVP en dur (recettes = dépenses * 1.3).
    """
    produit = ProduitStock.objects.create(
        ferme=ferme, nom="Aliment volaille", unite="KG",
        quantite_actuelle=0, seuil_alerte=10, prix_moyen_unitaire=Decimal('500'),
    )
    
    MouvementStock.objects.create(
        produit=produit,
        type='ENTREE',
        quantite=10,
        date=date.today(),
        prix_unitaire=Decimal('500'),
        created_by=admin_user,  # 🔥 'operateur' remplacé par 'created_by'
    )
    
    finances = get_finances(admin_user)
    assert finances['depenses'] == 5000.0
    assert finances['recettes'] == pytest.approx(6500.0)
    assert finances['marge'] == pytest.approx(1500.0)