from django.db.models import Sum, F
from decimal import Decimal
from datetime import date as date_today
from stocks.models import MouvementStock
from finances.models import Transaction


def get_finances(user):
    """
    Indicateurs financiers réels, cumul total depuis toujours (voir get_finances_mois
    pour la fenêtre mensuelle, ajoutée séparément — P15 étape 2 pour ne pas changer
    la signature de cette fonction déjà consommée par dashboard/views.py).

    Dépenses = achats de stock (MouvementStock, inchangé) + dépenses hors-stock (Transaction).
    Recettes = ventes réelles (Transaction) — remplace l'ancienne estimation à 1.3x (retirée P15).
    """
    ferme = user.ferme

    depenses_stock = MouvementStock.objects.filter(
        produit__ferme=ferme, type='ENTREE'
    ).aggregate(
        total=Sum(F('quantite') * F('prix_unitaire'))
    )['total'] or Decimal('0')

    depenses_hors_stock = Transaction.objects.filter(
        ferme=ferme, type='DEPENSE'
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    depenses = depenses_stock + depenses_hors_stock

    recettes = Transaction.objects.filter(
        ferme=ferme, type='RECETTE'
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    marge = recettes - depenses

    return {
        'recettes': float(recettes),
        'depenses': float(depenses),
        'marge': float(marge),
    }


def get_finances_mois(user, annee=None, mois=None):
    """
    Même logique que get_finances(), restreinte au mois donné (défaut : mois en cours).
    Fonction séparée plutôt que paramètre optionnel sur get_finances() — décision P15
    (plan section 3, décision 3) pour ne pas risquer de régression sur le code existant
    qui appelle déjà get_finances() sans argument.
    """
    today = date_today.today()
    annee = annee or today.year
    mois = mois or today.month
    ferme = user.ferme

    depenses_stock = MouvementStock.objects.filter(
        produit__ferme=ferme, type='ENTREE', date__year=annee, date__month=mois
    ).aggregate(total=Sum(F('quantite') * F('prix_unitaire')))['total'] or Decimal('0')

    depenses_hors_stock = Transaction.objects.filter(
        ferme=ferme, type='DEPENSE', date__year=annee, date__month=mois
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    depenses = depenses_stock + depenses_hors_stock

    recettes = Transaction.objects.filter(
        ferme=ferme, type='RECETTE', date__year=annee, date__month=mois
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    return {
        'recettes': float(recettes),
        'depenses': float(depenses),
        'marge': float(recettes - depenses),
    }


def get_depenses_par_produit(user):
    """
    Pour graphique : répartition des dépenses par produit
    """
    data = MouvementStock.objects.filter(
        produit__ferme=user.ferme,
        type='ENTREE',
        prix_unitaire__isnull=False
    ).values('produit__nom').annotate(
        total=Sum(F('quantite') * F('prix_unitaire'))
    ).order_by('-total')[:5]

    return {
        'labels': [d['produit__nom'] for d in data],
        'valeurs': [float(d['total'] or 0) for d in data]
    }
