# dashboard/services/kpi_service.py
from django.db.models import Sum, F
from decimal import Decimal
from datetime import date
from cheptel.models import Animal, RapportJournalier, Traitement
from stocks.models import ProduitStock
from cultures.models import CultureParcelle


def get_kpis(user):
    """Indicateurs clés du tableau de bord - V2 avec Stocks et Cultures"""
    ferme = user.ferme
    
    # ========== 1. CHEPTEL ==========
    # Animaux
    animaux = Animal.objects.filter(ferme=ferme)
    total_animaux = animaux.count()
    animaux_actifs = animaux.filter(statut='ACTIF').count()
    
    # Œufs
    today = date.today()
    rapports_mois = RapportJournalier.objects.filter(
        ferme=ferme,
        date__year=today.year,
        date__month=today.month
    )
    oeufs_mois = rapports_mois.aggregate(Sum('oeufs_pondus'))['oeufs_pondus__sum'] or 0
    
    rapport_aujourdhui = RapportJournalier.objects.filter(
        ferme=ferme,
        date=today
    ).first()
    oeufs_aujourdhui = rapport_aujourdhui.oeufs_pondus if rapport_aujourdhui else 0
    
    # Traitements
    traitements = Traitement.objects.filter(ferme=ferme)
    total_traitements = traitements.count()
    
    # Rapports
    total_rapports = RapportJournalier.objects.filter(ferme=ferme).count()
    
    # ========== 2. STOCKS ==========
    produits = ProduitStock.objects.filter(ferme=ferme)
    total_produits = produits.count()
    produits_alerte = produits.filter(quantite_actuelle__lte=F('seuil_alerte')).count()
    
    # Valeur estimée du stock
    valeur_stock = produits.aggregate(
        total=Sum(F('quantite_actuelle') * F('prix_moyen_unitaire'))
    )['total'] or Decimal('0')
    
    # ========== 3. CULTURES ==========
    cultures_parcelles = CultureParcelle.objects.filter(parcelle__ferme=ferme)
    cultures_en_cours = cultures_parcelles.filter(date_recolte_reelle__isnull=True).count()
    recoltes_prevues = cultures_parcelles.filter(
        date_recolte_prevue__isnull=False,
        date_recolte_reelle__isnull=True
    ).count()
    
    return {
        # Cheptel
        'total_animaux': total_animaux,
        'animaux_actifs': animaux_actifs,
        'oeufs_mois': oeufs_mois,
        'oeufs_aujourdhui': oeufs_aujourdhui,
        'total_traitements': total_traitements,
        'total_rapports': total_rapports,
        # Stocks
        'total_produits': total_produits,
        'produits_alerte': produits_alerte,
        'valeur_stock': float(valeur_stock),
        # Cultures
        'cultures_en_cours': cultures_en_cours,
        'recoltes_prevues': recoltes_prevues,
    }