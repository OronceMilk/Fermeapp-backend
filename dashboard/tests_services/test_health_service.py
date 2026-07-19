from dashboard.services.health_service import get_health_score, get_health_status

def test_score_parfait_sans_alerte():
    kpis = {'produits_alerte': 0, 'total_animaux': 10, 'animaux_actifs': 10, 'recoltes_prevues': 0}
    assert get_health_score(kpis) == 100

def test_penalite_produits_en_alerte():
    kpis = {'produits_alerte': 2, 'total_animaux': 0, 'animaux_actifs': 0, 'recoltes_prevues': 0}
    assert get_health_score(kpis) == 80

def test_penalite_plafonnee_a_40():
    kpis = {'produits_alerte': 10, 'total_animaux': 0, 'animaux_actifs': 0, 'recoltes_prevues': 0}
    assert get_health_score(kpis) == 60

def test_penalite_taux_actifs_bas():
    kpis = {'produits_alerte': 0, 'total_animaux': 10, 'animaux_actifs': 5, 'recoltes_prevues': 0}
    assert get_health_score(kpis) == 70

def test_score_ne_descend_jamais_sous_zero():
    kpis = {'produits_alerte': 10, 'total_animaux': 10, 'animaux_actifs': 0, 'recoltes_prevues': 10}
    assert get_health_score(kpis) >= 0

def test_statut_excellent():
    assert get_health_status(85)['label'] == 'Excellent'

def test_statut_critique():
    assert get_health_status(30)['label'] == 'Critique'