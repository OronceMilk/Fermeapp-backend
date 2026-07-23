import pytest
from cheptel.models import Animal, LotPondeuses
from cheptel.forms import LotForm
from cheptel.services import (
    get_animaux_ferme,
    get_stats_cheptel,
    get_lots_avec_comptage,
    get_rapports_ferme,
    get_stats_rapports_mois,
    creer_lot,
)
from datetime import date, timedelta
pytestmark = pytest.mark.django_db

def test_get_animaux_ferme_isole_par_ferme(ferme, ferme_autre, espece):
    Animal.objects.create(identifiant="A1", ferme=ferme, espece=espece, sexe="F")
    Animal.objects.create(identifiant="A2", ferme=ferme_autre, espece=espece, sexe="M")

    resultat = get_animaux_ferme(ferme)
    assert resultat.count() == 1
    assert resultat.first().identifiant == "A1"

def test_get_animaux_ferme_filtre_par_statut(ferme, espece):
    Animal.objects.create(identifiant="A1", ferme=ferme, espece=espece, sexe="F", statut="ACTIF")
    Animal.objects.create(identifiant="A2", ferme=ferme, espece=espece, sexe="M", statut="VENDU")

    resultat = get_animaux_ferme(ferme, statut="VENDU")
    assert resultat.count() == 1
    assert resultat.first().identifiant == "A2"

def test_get_stats_cheptel_compte_correctement(ferme, espece):
    Animal.objects.create(identifiant="A1", ferme=ferme, espece=espece, sexe="F", statut="ACTIF")
    Animal.objects.create(identifiant="A2", ferme=ferme, espece=espece, sexe="M", statut="DECEDE")
    Animal.objects.create(identifiant="A3", ferme=ferme, espece=espece, sexe="F", statut="VENDU")

    stats = get_stats_cheptel(ferme)
    assert stats == {'total': 3, 'actif': 1, 'decede': 1, 'vendu': 1}

def test_get_lots_avec_comptage_annotation_correcte(ferme, espece):
    from datetime import date
    lot = LotPondeuses.objects.create(
        nom="Lot X", ferme=ferme, espece=espece,
        nombre_sujets=10, date_mise_en_place=date.today(),
    )
    Animal.objects.create(identifiant="A1", ferme=ferme, espece=espece, sexe="F", lot=lot)
    Animal.objects.create(identifiant="A2", ferme=ferme, espece=espece, sexe="M", lot=lot)

    lots = get_lots_avec_comptage(ferme)
    assert lots.get(pk=lot.pk).nb_animaux == 2

def test_get_lots_avec_comptage_une_seule_requete(ferme, espece, django_assert_max_num_queries):
    """
    Preuve directe de la correction du N+1 : peu importe le nombre de lots,
    une seule requête doit être exécutée pour obtenir tous les comptages.
    """
    from datetime import date
    for i in range(5):
        LotPondeuses.objects.create(
            nom=f"Lot {i}", ferme=ferme, espece=espece,
            nombre_sujets=10, date_mise_en_place=date.today(),
        )

    with django_assert_max_num_queries(1):
        lots = list(get_lots_avec_comptage(ferme))
        for lot in lots:
            _ = lot.nb_animaux

from django.core.files.uploadedfile import SimpleUploadedFile
from cheptel.forms import AnimalForm
from cheptel.services import creer_animal, mettre_a_jour_animal


def test_creer_animal_assigne_ferme_et_createur(ferme, espece, admin_user):
    form = AnimalForm(data={
        'identifiant': 'AN-200', 'espece': espece.id, 'sexe': 'F', 'statut': 'ACTIF',
    }, user=admin_user)
    assert form.is_valid(), form.errors

    animal = creer_animal(form, ferme=ferme, createur=admin_user)

    assert animal.pk is not None
    assert animal.ferme == ferme
    assert animal.createur == admin_user


def test_creer_animal_pas_de_double_enregistrement(ferme, espece, admin_user):
    """Vérifie qu'un seul animal est créé — garde-fou direct contre le piège du double form.save()."""
    from cheptel.models import Animal
    form = AnimalForm(data={
        'identifiant': 'AN-201', 'espece': espece.id, 'sexe': 'M', 'statut': 'ACTIF',
    }, user=admin_user)
    assert form.is_valid(), form.errors

    creer_animal(form, ferme=ferme, createur=admin_user)

    assert Animal.objects.filter(identifiant='AN-201').count() == 1


def test_creer_animal_avec_photo_est_bien_persistee(ferme, espece, admin_user):
    """
    Le test le plus important du sprint : vérifie que le fichier photo est bien
    associé à l'instance après passage par le service, pas perdu en route.
    """
    photo = SimpleUploadedFile(
        "test_animal.jpg", b"contenu_image_factice", content_type="image/jpeg",
    )
    form = AnimalForm(
        data={'identifiant': 'AN-202', 'espece': espece.id, 'sexe': 'F', 'statut': 'ACTIF'},
        files={'photo': photo}, user=admin_user,
    )
    assert form.is_valid(), form.errors

    animal = creer_animal(form, ferme=ferme, createur=admin_user)

    assert animal.photo.name  # le nom du fichier stocké n'est pas vide
    assert 'test_animal' in animal.photo.name


def test_mettre_a_jour_animal_preserve_createur_original(ferme, espece, admin_user):
    from accounts.models import User
    # Créer un autre utilisateur (pas ADMIN, pour éviter la contrainte d'unicité)
    autre_user = User.objects.create_user(
        username="autre_user", email="autre@test.com", password="TestPass123!",
        ferme=ferme, role="EMPLOYE",  # 🔥 CHANGEMENT : EMPLOYE au lieu de ADMIN
    )
    from cheptel.models import Animal
    animal = Animal.objects.create(
        identifiant="AN-203", ferme=ferme, espece=espece, sexe="F", createur=admin_user,
    )

    form = AnimalForm(
        data={'identifiant': 'AN-203', 'espece': espece.id, 'sexe': 'F', 'statut': 'VENDU'},
        instance=animal, user=autre_user,
    )
    assert form.is_valid(), form.errors

    animal_maj = mettre_a_jour_animal(form, autre_user)

    assert animal_maj.createur == admin_user  # pas autre_user, malgré qui a fait la modification
    assert animal_maj.statut == 'VENDU'  # le reste de la modification s'applique bien

    from datetime import date, timedelta
from cheptel.forms import TraitementForm
from cheptel.services import get_traitements_ferme, get_alertes_rappel, creer_traitement


def test_get_traitements_ferme_isole_par_ferme(ferme, ferme_autre, animal, produit, admin_user):
    from cheptel.models import Animal, Traitement
    animal_autre_ferme = Animal.objects.create(
        identifiant="A-AUTRE", ferme=ferme_autre, espece=animal.espece, sexe="M",
    )
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        produit=produit, operateur=admin_user,
    )
    Traitement.objects.create(
        animal=animal_autre_ferme, ferme=ferme_autre, type="VACCIN", date=date.today(),
        produit=produit, operateur=admin_user,
    )

    resultat = get_traitements_ferme(ferme)
    assert resultat.count() == 1


def test_get_traitements_ferme_filtre_par_type(ferme, animal, produit, admin_user):
    from cheptel.models import Traitement
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        produit=produit, operateur=admin_user,
    )
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="TRAITEMENT", date=date.today(),
        produit=produit, operateur=admin_user,
    )

    resultat = get_traitements_ferme(ferme, type_filtre="VACCIN")
    assert resultat.count() == 1
    assert resultat.first().type == "VACCIN"


def test_get_alertes_rappel_respecte_la_fenetre_de_7_jours(ferme, animal, produit, admin_user):
    from cheptel.models import Traitement
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=3), produit=produit, operateur=admin_user,
    )
    Traitement.objects.create(
        animal=animal, ferme=ferme, type="VACCIN", date=date.today(),
        rappel_le=date.today() + timedelta(days=15), produit=produit, operateur=admin_user,
    )

    alertes = get_alertes_rappel(ferme)
    assert alertes.count() == 1


def test_creer_traitement_pas_de_double_enregistrement(ferme, animal, produit, admin_user):
    from cheptel.models import Traitement
    form = TraitementForm(data={
        'animal': animal.id, 'type': 'VACCIN', 'date': date.today(),
        'produit': produit.id, 'dose': '2ml',
    }, user=admin_user)
    assert form.is_valid(), form.errors

    creer_traitement(form, ferme=ferme, operateur=admin_user)

    assert Traitement.objects.filter(animal=animal, type='VACCIN').count() == 1

    from cheptel.services import get_rapports_ferme, get_stats_rapports_mois, creer_lot


def test_get_rapports_ferme_filtre_par_annee_et_mois(ferme, admin_user):
    from cheptel.models import RapportJournalier
    RapportJournalier.objects.create(ferme=ferme, date=date(2026, 3, 15), createur=admin_user)
    RapportJournalier.objects.create(ferme=ferme, date=date(2026, 4, 10), createur=admin_user)

    resultat = get_rapports_ferme(ferme, annee=2026, mois=3)
    assert resultat.count() == 1


def test_get_stats_rapports_mois_agrege_le_mois_en_cours(ferme, admin_user):
    from cheptel.models import RapportJournalier
    today = date.today()
    RapportJournalier.objects.create(
        ferme=ferme, date=today, createur=admin_user,
        nombre_morts=2, oeufs_pondus=50, aliment_kg=10,
    )
    RapportJournalier.objects.create(
        ferme=ferme, date=today - timedelta(days=1), createur=admin_user,
        nombre_morts=1, oeufs_pondus=40, aliment_kg=8,
    )

    stats = get_stats_rapports_mois(ferme)
    assert stats['total_morts_mois'] == 3
    assert stats['total_oeufs_mois'] == 90
    assert stats['moyenne_aliment'] == 9.0


def test_get_stats_rapports_mois_zero_si_aucun_rapport(ferme):
    stats = get_stats_rapports_mois(ferme)
    assert stats == {'total_morts_mois': 0, 'total_oeufs_mois': 0, 'moyenne_aliment': 0}

    from cheptel.forms import LotForm
from cheptel.services import creer_lot


def test_creer_lot_pas_de_double_enregistrement(ferme, espece, admin_user):
    from cheptel.models import LotPondeuses
    form = LotForm(data={
        'nom': 'Lot Test Service', 'espece': espece.id,
        'nombre_sujets': 20, 'date_mise_en_place': date.today(),
    }, user=admin_user)
    assert form.is_valid(), form.errors

    creer_lot(form, ferme=ferme, createur=admin_user)

    assert LotPondeuses.objects.filter(nom='Lot Test Service').count() == 1