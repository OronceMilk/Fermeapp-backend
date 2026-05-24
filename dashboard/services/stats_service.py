# dashboard/services/stats_service.py
from django.db.models import Count, Sum, F
from datetime import date, timedelta
from cheptel.models import RapportJournalier, Animal
from stocks.models import MouvementStock, ProduitStock


def get_production_data(user):
    """Graphique 1 : Évolution de la ponte (30 derniers jours)"""
    ferme = user.ferme
    today = date.today()
    start_date = today - timedelta(days=29)
    
    rapports = RapportJournalier.objects.filter(
        ferme=ferme,
        date__gte=start_date,
        date__lte=today
    ).order_by('date')
    
    dates = []
    valeurs = []
    
    # Créer un dictionnaire date -> oeufs
    oeufs_par_jour = {r.date: r.oeufs_pondus for r in rapports}
    
    # Remplir tous les jours de la période
    current = start_date
    while current <= today:
        dates.append(current.strftime('%d/%m'))
        valeurs.append(oeufs_par_jour.get(current, 0))
        current += timedelta(days=1)
    
    return {
        'dates': dates,
        'valeurs': valeurs
    }


def get_animaux_par_espece(user):
    """Graphique 2 : Répartition des animaux par espèce (camembert)"""
    ferme = user.ferme
    
    data = Animal.objects.filter(
        ferme=ferme,
        statut='ACTIF'
    ).values('espece__nom').annotate(
        count=Count('id')
    ).order_by('-count')
    
    labels = [item['espece__nom'] for item in data]
    valeurs = [item['count'] for item in data]
    
    return {
        'labels': labels,
        'valeurs': valeurs
    }


def get_stock_evolution(user):
    """Graphique 3 : Évolution des stocks (7 derniers jours)"""
    ferme = user.ferme
    today = date.today()
    dates = []
    entrees = []
    sorties = []
    
    # Parcourir les 7 derniers jours + aujourd'hui
    for i in range(7, -1, -1):
        d = today - timedelta(days=i)
        dates.append(d.strftime('%d/%m'))
        
        # Entrées du jour
        e = MouvementStock.objects.filter(
            produit__ferme=ferme,
            date=d,
            type='ENTREE'
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        # Sorties du jour
        s = MouvementStock.objects.filter(
            produit__ferme=ferme,
            date=d,
            type='SORTIE'
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        entrees.append(float(e))
        sorties.append(float(s))
    
    return {
        'dates': dates,
        'entrees': entrees,
        'sorties': sorties
    }


def get_depenses_par_produit(user):
    """
    Graphique 4 : Répartition des dépenses par produit (Top 5)
    🔥 Utilise F() pour le calcul correct du montant total
    """
    ferme = user.ferme
    
    data = MouvementStock.objects.filter(
        produit__ferme=ferme,
        type='ENTREE',
        prix_unitaire__isnull=False
    ).values('produit__nom').annotate(
        total=Sum(F('quantite') * F('prix_unitaire'))
    ).order_by('-total')[:5]
    
    return {
        'labels': [d['produit__nom'] for d in data],
        'valeurs': [float(d['total'] or 0) for d in data]
    }


def get_valeur_stock_par_produit(user):
    """
    Graphique optionnel : Valeur du stock par produit (Top 5)
    """
    ferme = user.ferme
    
    data = ProduitStock.objects.filter(
        ferme=ferme,
        prix_moyen_unitaire__isnull=False,
        quantite_actuelle__gt=0
    ).values('nom').annotate(
        valeur=Sum(F('quantite_actuelle') * F('prix_moyen_unitaire'))
    ).order_by('-valeur')[:5]
    
    return {
        'labels': [d['nom'] for d in data],
        'valeurs': [float(d['valeur'] or 0) for d in data]
    }