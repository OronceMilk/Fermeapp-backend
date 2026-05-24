# dashboard/services/activity_service.py
from cheptel.models import Animal, RapportJournalier, Traitement
from stocks.models import MouvementStock
from cultures.models import ActiviteAgricole


def get_recent_activities(user):
    """Journal des 20 dernières actions (multi-modules) avec tri par datetime complet"""
    ferme = user.ferme
    activites = []
    
    # ========== 1. CHEPTEL - Animaux ajoutés ==========
    animaux_recents = Animal.objects.filter(
        ferme=ferme
    ).order_by('-created_at')[:4]
    
    for a in animaux_recents:
        activites.append({
            'type': 'animal',
            'module': 'cheptel',
            'action': '➕ Ajout animal',
            'detail': f"{a.identifiant} - {a.nom or a.espece.nom}",
            'datetime': a.created_at,
            'date': a.created_at.date(),
            'heure': a.created_at.strftime('%H:%M')
        })
    
    # ========== 2. CHEPTEL - Rapports journaliers ==========
    rapports_recents = RapportJournalier.objects.filter(
        ferme=ferme
    ).order_by('-created_at')[:4]
    
    for r in rapports_recents:
        activites.append({
            'type': 'rapport',
            'module': 'cheptel',
            'action': '📋 Rapport journalier',
            'detail': f"{r.oeufs_pondus} œufs, {r.nombre_morts} morts",
            'datetime': r.created_at,
            'date': r.created_at.date(),
            'heure': r.created_at.strftime('%H:%M')
        })
    
    # ========== 3. CHEPTEL - Traitements ==========
    traitements_recents = Traitement.objects.filter(
        ferme=ferme
    ).order_by('-created_at')[:4]
    
    for t in traitements_recents:
        activites.append({
            'type': 'traitement',
            'module': 'cheptel',
            'action': f"💊 {t.get_type_display()}",
            'detail': f"{t.animal.identifiant} - {t.produit.nom}",
            'datetime': t.created_at,
            'date': t.created_at.date(),
            'heure': t.created_at.strftime('%H:%M')
        })
    
    # ========== 4. STOCKS - Mouvements (entrées/sorties) ==========
    mouvements_recents = MouvementStock.objects.filter(
        produit__ferme=ferme
    ).order_by('-created_at')[:4]
    
    for m in mouvements_recents:
        direction = "📥 Entrée" if m.type == 'ENTREE' else "📤 Sortie"
        activites.append({
            'type': 'mouvement',
            'module': 'stock',
            'action': direction,
            'detail': f"{m.produit.nom}: {m.quantite} {m.produit.get_unite_display()}",
            'datetime': m.created_at,
            'date': m.created_at.date(),
            'heure': m.created_at.strftime('%H:%M')
        })
    
    # ========== 5. CULTURES - Activités agricoles ==========
    activites_agricoles = ActiviteAgricole.objects.filter(
        culture_parcelle__parcelle__ferme=ferme
    ).order_by('-created_at')[:4]
    
    for a in activites_agricoles:
        activites.append({
            'type': 'activite_agricole',
            'module': 'cultures',
            'action': f"🚜 {a.get_type_display()}",
            'detail': f"{a.culture_parcelle.culture.nom} - {a.culture_parcelle.parcelle.nom}",
            'datetime': a.created_at,
            'date': a.created_at.date(),
            'heure': a.created_at.strftime('%H:%M')
        })
    
    # 🔥 TRI PAR DATETIME COMPLET (plus récent d'abord)
    activites.sort(key=lambda x: x['datetime'], reverse=True)
    
    return activites[:20]  # Augmenté à 20 pour couvrir plus d'activités