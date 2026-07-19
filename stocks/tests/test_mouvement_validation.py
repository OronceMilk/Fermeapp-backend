import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from stocks.models import MouvementStock
from stocks.services import StockService

pytestmark = pytest.mark.django_db

def test_creation_orm_directe_quantite_negative_non_bloquee(produit_stock):
    """
    ⚠️ Documente un comportement réel : MouvementStock.clean() existe mais
    n'est jamais appelé automatiquement (pas de save() qui appelle full_clean()).
    Passer par l'ORM directement (hors StockService) laisse passer une quantité négative.
    """
    m = MouvementStock.objects.create(
        produit=produit_stock, type="ENTREE", quantite=Decimal("-5.00"),
    )
    assert m.pk is not None  # aucune erreur levée, contrairement à ce que clean() prévoit

def test_full_clean_explicite_detecte_bien_quantite_negative(produit_stock):
    m = MouvementStock(produit=produit_stock, type="ENTREE", quantite=Decimal("-5.00"))
    with pytest.raises(ValidationError):
        m.full_clean()

def test_service_creer_mouvement_protege_bien_malgre_le_gap_modele(produit_stock, admin_user):
    """Le service, lui, protège correctement — la faille ne concerne que l'ORM direct."""
    with pytest.raises(ValueError):
        StockService.creer_mouvement(
            produit_id=produit_stock.id, type_mouvement="ENTREE",
            quantite=Decimal("-5.00"), user=admin_user,
        )