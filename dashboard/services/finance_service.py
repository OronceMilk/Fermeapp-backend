# dashboard/services/finance_service.py
from django.db.models import Sum, F
from decimal import Decimal
from stocks.models import MouvementStock


def get_finances(user):
    """
    Calcule les indicateurs financiers de base.
    🔥 Version MVP - recettes estimées à 30% de marge
    (à enrichir avec module Ventes plus tard)
    """
    mouvements = MouvementStock.objects.filter(
        produit__ferme=user.ferme
    )
    
    # Dépenses = entrées (achats)
    depenses = mouvements.filter(type='ENTREE').aggregate(
        total=Sum(F('quantite') * F('prix_unitaire'))
    )['total'] or Decimal('0')
    
    # 🔥 Recettes estimées (marge 30%)
    # À dire en soutenance : "En attendant le module Ventes, on estime la marge à 30%"
    recettes = depenses * Decimal('1.3')
    
    marge = recettes - depenses
    
    return {
        'recettes': float(recettes),
        'depenses': float(depenses),
        'marge': float(marge),
    }


def get_depenses_par_produit(user):
    """
    Pour graphique : répartition des dépenses par produit
    """
    data = MouvementStock.objects.filter(
        produit__ferme=user.ferme,
        type='ENTREE',
        prix_unitaire__isnull=False
    ).values('produit__nom').annotate(
        total=Sum(F('quantite') * F('prix_unitaire'))
    ).order_by('-total')[:5]
    
    return {
        'labels': [d['produit__nom'] for d in data],
        'valeurs': [float(d['total'] or 0) for d in data]
    }