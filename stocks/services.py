# stocks/services.py
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import ProduitStock, MouvementStock


class StockService:
    """
    Service métier pour la gestion des stocks.
    Centralise toute la logique pour éviter les incohérences.
    """
    
    @staticmethod
    @transaction.atomic
    def creer_mouvement(produit_id, type_mouvement, quantite, user, **kwargs):
        """
        Crée un mouvement de stock avec verrouillage de ligne.
        🔥 Utilise select_for_update() pour éviter les races conditions.
        """
        
        # 🔥 Verrouillage de la ligne en base (prévention concurrence)
        produit = ProduitStock.objects.select_for_update().get(id=produit_id)
        
        # Validation
        if quantite <= 0:
            raise ValueError("La quantité doit être positive.")
        
        if type_mouvement == 'SORTIE' and produit.quantite_actuelle < quantite:
            raise ValueError(
                f"Stock insuffisant. Disponible: {produit.quantite_actuelle} {produit.get_unite_display()}"
            )
        
        # Enregistrement du stock avant modification
        stock_avant = produit.quantite_actuelle
        
        # Mise à jour du stock
        if type_mouvement == 'ENTREE':
            produit.quantite_actuelle += quantite
        else:
            produit.quantite_actuelle -= quantite
        
        produit.save()
        
        # Création du mouvement avec traçabilité
        mouvement = MouvementStock.objects.create(
            produit=produit,
            type=type_mouvement,
            quantite=quantite,
            date=kwargs.get('date') or timezone.now().date(),
            motif=kwargs.get('motif', ''),
            reference=kwargs.get('reference', ''),
            prix_unitaire=kwargs.get('prix_unitaire', None),
            stock_avant=stock_avant,
            stock_apres=produit.quantite_actuelle,
            created_by=user
        )
        
        return mouvement
    
    @staticmethod
    @transaction.atomic
    def annuler_mouvement(mouvement_id, user):
        """
        Annule un mouvement existant en créant un mouvement inverse.
        🔥 Alternative à la suppression : traçabilité totale.
        """
        mouvement = MouvementStock.objects.select_for_update().get(id=mouvement_id)
        
        type_inverse = 'ENTREE' if mouvement.type == 'SORTIE' else 'SORTIE'
        
        return StockService.creer_mouvement(
            produit_id=mouvement.produit.id,
            type_mouvement=type_inverse,
            quantite=mouvement.quantite,
            user=user,
            motif=f"Annulation du mouvement #{mouvement.id}",
            reference=mouvement.reference
        )
    
    @staticmethod
    def get_stock_calcule(produit_id):
        """
        🔥 Option expert : recalcule le stock à partir des mouvements.
        Permet un audit en cas de doute sur l'intégrité des données.
        """
        from django.db.models import Sum
        
        produit = ProduitStock.objects.get(id=produit_id)
        
        entrees = produit.mouvements.filter(type='ENTREE').aggregate(
            total=Sum('quantite')
        )['total'] or Decimal(0)
        
        sorties = produit.mouvements.filter(type='SORTIE').aggregate(
            total=Sum('quantite')
        )['total'] or Decimal(0)
        
        return entrees - sorties
    
    @staticmethod
    def get_produits_en_alerte(ferme):
        """Retourne les produits dont le stock est sous le seuil d'alerte"""
        return ProduitStock.objects.filter(
            ferme=ferme,
            quantite_actuelle__lte=F('seuil_alerte')
        )
    
    @staticmethod
    def get_depenses_totales(ferme, annee=None, mois=None):
        """Pour dashboard financier - total des achats"""
        from django.db.models import Sum, Q
        
        queryset = MouvementStock.objects.filter(
            produit__ferme=ferme,
            type='ENTREE',
            prix_unitaire__isnull=False
        )
        
        if annee:
            queryset = queryset.filter(date__year=annee)
        if mois:
            queryset = queryset.filter(date__month=mois)
        
        result = queryset.aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total']
        
        return result or Decimal(0)
