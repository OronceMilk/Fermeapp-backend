import pytest
from decimal import Decimal
from stocks.models import ProduitStock

@pytest.fixture
def produit_stock(ferme):
    return ProduitStock.objects.create(
        ferme=ferme, nom="Semences maïs", unite="KG",
        quantite_actuelle=Decimal("20.00"), seuil_alerte=Decimal("5.00"),
    )