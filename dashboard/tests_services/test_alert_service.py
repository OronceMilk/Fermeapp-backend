import pytest
from datetime import date, timedelta
from dashboard.services.alert_service import get_alertes
from cheptel.models import Traitement

pytestmark = pytest.mark.django_db

def test_alerte_vaccin_generee_dans_les_7_jours(ferme, animal, produit, admin_user):
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=3), produit=produit, operateur=admin_user,
    )
    alertes = get_alertes(admin_user)
    types = [a['type'] for a in alertes]
    assert 'vaccin' in types

def test_pas_alerte_vaccin_hors_fenetre_7_jours(ferme, animal, produit, admin_user):
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=20), produit=produit, operateur=admin_user,
    )
    alertes = get_alertes(admin_user)
    types = [a['type'] for a in alertes]
    assert 'vaccin' not in types

def test_tri_priorite_danger_avant_info(ferme, animal, produit, admin_user):
    from cheptel.models import RapportJournalier
    RapportJournalier.objects.create(ferme=ferme, date=date.today(), sujets_malades=2, createur=admin_user)
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=6), produit=produit, operateur=admin_user,
    )
    alertes = get_alertes(admin_user)
    niveaux = [a['niveau'] for a in alertes]
    assert niveaux.index('danger') < niveaux.index('info')