import threading
import pytest
from decimal import Decimal
from django.db import connections
from stocks.models import ProduitStock
from stocks.services import StockService


@pytest.mark.django_db(transaction=True)
def test_deux_sorties_concurrentes_ne_produisent_jamais_stock_negatif(ferme, admin_user):
    """
    Test de concurrence réel : deux threads, deux connexions DB séparées,
    synchronisés pour démarrer en même temps sur le MÊME produit.
    transaction=True est indispensable : sans ça, Django wrappe le test dans
    une seule transaction non-committée, et select_for_update() ne peut pas
    produire de vraie contention entre deux threads.
    """
    produit = ProduitStock.objects.create(
        ferme=ferme, nom="Aliment concurrence", unite="KG",
        quantite_actuelle=Decimal("10.00"), seuil_alerte=Decimal("2.00"),
    )

    resultats = {"succes": 0, "echecs": 0}
    barriere = threading.Barrier(2)  # force les deux threads à démarrer au même instant

    def sortie_concurrente():
        barriere.wait()
        try:
            StockService.creer_mouvement(
                produit_id=produit.id, type_mouvement="SORTIE",
                quantite=Decimal("6.00"), user=admin_user,
            )
            resultats["succes"] += 1
        except ValueError:
            resultats["echecs"] += 1
        finally:
            connections.close_all()  # ferme la connexion propre au thread

    threads = [threading.Thread(target=sortie_concurrente) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    produit.refresh_from_db()

    # Stock initial 10, deux sorties de 6 demandées : la seconde DOIT échouer
    # (6 restant après la première < 6 demandé par la seconde).
    assert resultats["succes"] == 1
    assert resultats["echecs"] == 1
    assert produit.quantite_actuelle == Decimal("4.00")
    assert produit.quantite_actuelle >= 0  # la garantie la plus importante du test