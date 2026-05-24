# dashboard/services/health_service.py

def get_health_score(kpis):
    """
    Calcule un score de santé globale (0-100%).
    🔥 Très apprécié en soutenance
    """
    score = 100
    
    # Pénalité pour produits en alerte
    if kpis.get('produits_alerte', 0) > 0:
        score -= min(40, kpis['produits_alerte'] * 10)
    
    # Pénalité pour animaux non actifs
    total_animaux = kpis.get('total_animaux', 0)
    animaux_actifs = kpis.get('animaux_actifs', 0)
    if total_animaux > 0:
        taux_actifs = (animaux_actifs / total_animaux) * 100
        if taux_actifs < 80:
            score -= 30
    
    # Pénalité pour cultures non récoltées
    recoltes_prevues = kpis.get('recoltes_prevues', 0)
    if recoltes_prevues > 5:
        score -= 20
    
    return max(score, 0)


def get_health_status(score):
    """Retourne le statut qualitatif"""
    if score >= 80:
        return {'label': 'Excellent', 'color': 'success', 'icon': '🟢'}
    elif score >= 50:
        return {'label': 'Attention', 'color': 'warning', 'icon': '🟡'}
    else:
        return {'label': 'Critique', 'color': 'danger', 'icon': '🔴'}