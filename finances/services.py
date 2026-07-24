from decimal import Decimal
from django.db.models import Sum
from .models import Transaction


def creer_transaction(ferme, createur, type, categorie, montant, date=None, commentaire=''):
    """Enregistre une transaction financière (vente ou dépense hors-stock)."""
    kwargs = {
        'ferme': ferme, 'createur': createur, 'type': type,
        'categorie': categorie, 'montant': montant, 'commentaire': commentaire,
    }
    if date:
        kwargs['date'] = date
    return Transaction.objects.create(**kwargs)


def get_transactions_ferme(ferme, type_filtre=None, categorie=None):
    """Liste des transactions d'une ferme, avec filtres optionnels."""
    queryset = Transaction.objects.filter(ferme=ferme)
    if type_filtre:
        queryset = queryset.filter(type=type_filtre)
    if categorie:
        queryset = queryset.filter(categorie=categorie)
    return queryset


def get_total_par_type(ferme, type_transaction, annee=None, mois=None):
    """Somme des transactions d'un type donné, avec fenêtre temporelle optionnelle."""
    queryset = Transaction.objects.filter(ferme=ferme, type=type_transaction)
    if annee:
        queryset = queryset.filter(date__year=annee)
    if mois:
        queryset = queryset.filter(date__month=mois)
    return queryset.aggregate(total=Sum('montant'))['total'] or Decimal('0')