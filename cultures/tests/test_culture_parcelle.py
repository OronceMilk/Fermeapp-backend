import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cultures.models import CultureParcelle

pytestmark = pytest.mark.django_db

def test_creation_orm_directe_valide_desormais_automatiquement(parcelle, culture):
    """
    Sprint 11 (P1.7) : CultureParcelle appelle maintenant full_clean() dans save(),
    alignement avec le pattern cheptel. Une incohérence de dates est désormais
    bloquée même via l'ORM direct, pas seulement via les formulaires web.
    """
    with pytest.raises(ValidationError):
        CultureParcelle.objects.create(
            parcelle=parcelle, culture=culture,
            date_semis=date.today(),
            date_recolte_prevue=date.today() - timedelta(days=5),
        )

def test_full_clean_explicite_detecte_bien_incoherence(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today(),
        date_recolte_prevue=date.today() - timedelta(days=5),
    )
    with pytest.raises(ValidationError):
        cp.full_clean()

def test_recolte_reelle_avant_semis_detectee_par_full_clean(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today(),
        date_recolte_reelle=date.today() - timedelta(days=1),
    )
    with pytest.raises(ValidationError):
        cp.full_clean()

def test_dates_coherentes_acceptees(parcelle, culture):
    cp = CultureParcelle(
        parcelle=parcelle, culture=culture,
        date_semis=date.today() - timedelta(days=60),
        date_recolte_prevue=date.today() + timedelta(days=30),
    )
    cp.full_clean()


def test_creation_via_formulaire_fonctionne_toujours(parcelle, culture, admin_user):
    """
    Non-régression : le chemin normal (formulaire web) fonctionnait déjà avant ce
    correctif et doit continuer à fonctionner de façon identique après.
    """
    from cultures.forms import CultureParcelleForm

    form = CultureParcelleForm(data={
        'parcelle': parcelle.id,
        'culture': culture.id,
        'date_semis': date.today(),
    }, user=admin_user)
    assert form.is_valid(), form.errors
    cp = form.save()
    assert cp.pk is not None