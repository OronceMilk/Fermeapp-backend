# cheptel/services.py
from datetime import date, timedelta

from django.db.models import Count

from .models import Animal, LotPondeuses, Traitement


def get_animaux_ferme(ferme, statut=None, espece_id=None, lot_id=None):
    """
    Retourne les animaux d'une ferme, avec filtres optionnels.
    Centralise ce qui était dans AnimalListView.get_queryset().
    """
    queryset = Animal.objects.filter(ferme=ferme).select_related('espece', 'lot')

    if statut:
        queryset = queryset.filter(statut=statut)
    if espece_id:
        queryset = queryset.filter(espece_id=espece_id)
    if lot_id:
        queryset = queryset.filter(lot_id=lot_id)

    return queryset


def get_stats_cheptel(ferme):
    """
    Statistiques agrégées du cheptel d'une ferme.
    Centralise ce qui était dans AnimalListView.get_context_data().
    """
    animaux_ferme = Animal.objects.filter(ferme=ferme)
    return {
        'total': animaux_ferme.count(),
        'actif': animaux_ferme.filter(statut='ACTIF').count(),
        'decede': animaux_ferme.filter(statut='DECEDE').count(),
        'vendu': animaux_ferme.filter(statut='VENDU').count(),
    }


def get_lots_avec_comptage(ferme):
    """
    Retourne les lots d'une ferme, chacun annoté du nombre d'animaux qu'il contient.
    Remplace la boucle N+1 de LotListView.get_context_data() par une seule requête
    (un JOIN + GROUP BY exécuté côté base de données, pas côté Python).
    """
    return LotPondeuses.objects.filter(ferme=ferme).annotate(
        nb_animaux=Count('animaux')
    ).order_by('-date_mise_en_place')

def creer_animal(form, ferme, createur):
    """
    Enregistre un nouvel animal à partir d'un formulaire déjà validé.
    Assignation des attributs AVANT l'appel à .save() — crucial pour la photo.
    """
    form.instance.ferme = ferme
    form.instance.createur = createur
    return form.save()


def mettre_a_jour_animal(form, user):
    """
    Met à jour un animal existant, en préservant le createur original.
    """
    instance = form.save(commit=False)
    if instance.pk:
        original = Animal.objects.get(pk=instance.pk)
        instance.createur = original.createur
    else:
        instance.createur = user
    instance.save()
    return instance


def get_traitements_ferme(ferme, type_filtre=None, animal_id=None):
    animaux_ferme = Animal.objects.filter(ferme=ferme)
    queryset = Traitement.objects.filter(
        animal__in=animaux_ferme
    ).select_related('animal', 'produit', 'operateur').order_by('-date')
    if type_filtre:
        queryset = queryset.filter(type=type_filtre)
    if animal_id:
        queryset = queryset.filter(animal_id=animal_id)
    return queryset

def get_alertes_rappel(ferme, jours=7):
    today = date.today()
    animaux_ferme = Animal.objects.filter(ferme=ferme)
    return Traitement.objects.filter(
        animal__in=animaux_ferme,
        rappel_le__isnull=False,
        rappel_le__gte=today,
        rappel_le__lte=today + timedelta(days=jours),
    ).select_related('animal')

def creer_traitement(form, ferme, operateur):
    form.instance.ferme = ferme
    form.instance.operateur = operateur
    return form.save()
from django.db.models import Sum, Avg
from .models import RapportJournalier

def get_rapports_ferme(ferme, annee=None, mois=None):
    queryset = RapportJournalier.objects.filter(ferme=ferme).order_by('-date')
    if annee:
        queryset = queryset.filter(date__year=annee)
    if mois:
        queryset = queryset.filter(date__month=mois)
    return queryset

def get_stats_rapports_mois(ferme):
    today = date.today()
    rapports_mois = RapportJournalier.objects.filter(
        ferme=ferme, date__year=today.year, date__month=today.month,
    )
    return {
        'total_morts_mois': rapports_mois.aggregate(Sum('nombre_morts'))['nombre_morts__sum'] or 0,
        'total_oeufs_mois': rapports_mois.aggregate(Sum('oeufs_pondus'))['oeufs_pondus__sum'] or 0,
        'moyenne_aliment': rapports_mois.aggregate(Avg('aliment_kg'))['aliment_kg__avg'] or 0,
    }

def creer_lot(form, ferme, createur):
    form.instance.ferme = ferme
    form.instance.createur = createur
    return form.save()