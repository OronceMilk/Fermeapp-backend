# dashboard/services/alert_service.py
from datetime import date, timedelta
from django.db.models import F
from cheptel.models import Traitement, RapportJournalier
from stocks.models import ProduitStock
from cultures.models import CultureParcelle


def get_alertes(user):
    """Alertes multi-modules avec priorisation (danger > warning > info)"""
    ferme = user.ferme
    today = date.today()
    alertes = []
    
    # ========== 1. CHEPTEL - Vaccins à venir (7 jours) ==========
    vaccins_proches = Traitement.objects.filter(
        ferme=ferme,
        type='VACCIN',
        rappel_le__isnull=False,
        rappel_le__gte=today,
        rappel_le__lte=today + timedelta(days=7)
    ).select_related('animal', 'produit')
    
    for v in vaccins_proches:
        jours = (v.rappel_le - today).days
        alertes.append({
            'type': 'vaccin',
            'module': 'cheptel',
            'niveau': 'warning' if jours <= 2 else 'info',
            'message': f"💉 Vaccin {v.produit.nom} pour {v.animal.identifiant} dans {jours} jour(s)",
            'date': v.rappel_le
        })
    
    # ========== 2. CHEPTEL - Animaux malades (3 jours) ==========
    rapports_recents = RapportJournalier.objects.filter(
        ferme=ferme,
        date__gte=today - timedelta(days=3),
        sujets_malades__gt=0
    )
    
    for r in rapports_recents:
        alertes.append({
            'type': 'maladie',
            'module': 'cheptel',
            'niveau': 'danger',
            'message': f"🤒 {r.sujets_malades} animal(aux) malade(s) signalé(s) le {r.date.strftime('%d/%m/%Y')}",
            'date': r.date
        })
    
    # ========== 3. STOCKS - Alertes stock bas (optimisé) ==========
    # Évite une boucle sur tous les produits
    produits_alerte = ProduitStock.objects.filter(
        ferme=ferme,
        quantite_actuelle__lte=F('seuil_alerte'),
        quantite_actuelle__gt=0
    )
    
    for p in produits_alerte:
        alertes.append({
            'type': 'stock_bas',
            'module': 'stock',
            'niveau': 'warning',
            'message': f"⚠️ Stock bas : {p.nom} ({p.quantite_actuelle} {p.get_unite_display()})",
            'date': today
        })
    
    # ========== 4. STOCKS - Rupture de stock ==========
    produits_rupture = ProduitStock.objects.filter(
        ferme=ferme,
        quantite_actuelle=0
    )
    
    for p in produits_rupture:
        alertes.append({
            'type': 'rupture',
            'module': 'stock',
            'niveau': 'danger',
            'message': f"❌ Rupture de stock : {p.nom}",
            'date': today
        })
    
    # ========== 5. CULTURES - Récoltes à venir (14 jours) ==========
    recoltes_proches = CultureParcelle.objects.filter(
        parcelle__ferme=ferme,
        date_recolte_prevue__isnull=False,
        date_recolte_reelle__isnull=True,
        date_recolte_prevue__gte=today,
        date_recolte_prevue__lte=today + timedelta(days=14)
    ).select_related('parcelle', 'culture')
    
    for r in recoltes_proches:
        jours = (r.date_recolte_prevue - today).days
        alertes.append({
            'type': 'recolte',
            'module': 'cultures',
            'niveau': 'info',
            'message': f"🌾 Récolte de {r.culture.nom} sur {r.parcelle.nom} dans {jours} jour(s)",
            'date': r.date_recolte_prevue
        })
    
    # ========== 6. TRI INTELLIGENT (priorité niveau + date) ==========
    priority = {'danger': 1, 'warning': 2, 'info': 3}
    alertes.sort(key=lambda x: (priority[x['niveau']], x['date']))
    
    return alertes[:15]  # Augmenté à 15 pour tenir compte des nouveaux types