# stocks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.core.paginator import Paginator
from .models import ProduitStock, MouvementStock
from .forms import ProduitStockForm, EntreeStockForm, SortieStockForm, MouvementFiltreForm
from .services import StockService


# ==============================
# DÉCORATEUR DE SÉCURITÉ
# ==============================

def admin_required(view_func):
    """Vérifie que l'utilisateur a le rôle ADMIN"""
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            messages.error(request, "⛔ Accès refusé. Cette action est réservée aux administrateurs.")
            return redirect('stocks:produit_list')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==============================
# PRODUITS STOCK (CRUD)
# ==============================

@login_required
def stock_dashboard(request):
    """Vue synthétique des stocks avec partials HTMX."""
    produits = ProduitStock.objects.filter(ferme=request.user.ferme)
    produits_alerte = produits.filter(quantite_actuelle__lte=F('seuil_alerte'))

    context = {
        'aliments': produits,
        'semences': [],
        'produits_en_alerte': produits_alerte.count(),
        'total_produits': produits.count(),
    }
    return render(request, 'stocks/stocks.html', context)


@login_required
def aliments_partial(request):
    """Table HTMX des intrants en stock."""
    aliments = ProduitStock.objects.filter(ferme=request.user.ferme)
    return render(request, 'stocks/aliments_table.html', {'aliments': aliments})


@login_required
def semences_partial(request):
    """Table HTMX de la banque de semences.

    Aucun modèle Semence n'existe encore dans l'application; on renvoie donc un
    état vide fiable au lieu de laisser l'onglet tomber en 404.
    """
    return render(request, 'stocks/semences_table.html', {'semences': []})


@login_required
def produit_list(request):
    """Liste des produits en stock"""
    produits = ProduitStock.objects.filter(ferme=request.user.ferme)
    
    # Filtre par alerte
    alerte_only = request.GET.get('alerte')
    if alerte_only == '1':
        produits = produits.filter(quantite_actuelle__lte=F('seuil_alerte'))
    
    # Pagination
    paginator = Paginator(produits, 20)
    page_number = request.GET.get('page')
    produits_page = paginator.get_page(page_number)
    
    context = {
        'produits': produits_page,
        'produits_en_alerte': produits.filter(quantite_actuelle__lte=F('seuil_alerte')).count(),
    }
    return render(request, 'stocks/produit_list.html', context)


@login_required
@admin_required
def produit_create(request):
    """Créer un nouveau produit en stock"""
    if request.method == 'POST':
        form = ProduitStockForm(request.POST)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.ferme = request.user.ferme
            produit.save()
            messages.success(request, f"✅ Produit '{produit.nom}' créé avec succès.")
            return redirect('stocks:produit_list')
    else:
        form = ProduitStockForm()
    
    return render(request, 'stocks/produit_form.html', {'form': form, 'title': 'Ajouter un produit'})


@login_required
@admin_required
def produit_update(request, pk):
    """Modifier un produit existant"""
    produit = get_object_or_404(ProduitStock, pk=pk, ferme=request.user.ferme)
    
    if request.method == 'POST':
        form = ProduitStockForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Produit '{produit.nom}' modifié avec succès.")
            return redirect('stocks:produit_list')
    else:
        form = ProduitStockForm(instance=produit)
    
    return render(request, 'stocks/produit_form.html', {'form': form, 'title': 'Modifier le produit'})


@login_required
@admin_required
def produit_delete(request, pk):
    """Supprimer un produit (uniquement s'il n'a pas de mouvements)"""
    produit = get_object_or_404(ProduitStock, pk=pk, ferme=request.user.ferme)
    
    if request.method == 'POST':
        if produit.mouvements.count() > 0:
            messages.error(request, f"❌ Impossible de supprimer '{produit.nom}' car il a {produit.mouvements.count()} mouvement(s) associé(s).")
        else:
            produit.delete()
            messages.success(request, f"🗑️ Produit '{produit.nom}' supprimé avec succès.")
        return redirect('stocks:produit_list')
    
    return render(request, 'stocks/produit_confirm_delete.html', {'object': produit})


# ==============================
# MOUVEMENTS DE STOCK
# ==============================

@login_required
def mouvement_list(request):
    """Liste des mouvements de stock avec filtres"""
    mouvements = MouvementStock.objects.filter(
        produit__ferme=request.user.ferme
    ).select_related('produit', 'created_by')
    
    # Formulaire de filtre
    form = MouvementFiltreForm(request.GET or None, user=request.user)
    
    if form.is_valid():
        if form.cleaned_data.get('produit'):
            mouvements = mouvements.filter(produit=form.cleaned_data['produit'])
        if form.cleaned_data.get('type'):
            mouvements = mouvements.filter(type=form.cleaned_data['type'])
        if form.cleaned_data.get('date_debut'):
            mouvements = mouvements.filter(date__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            mouvements = mouvements.filter(date__lte=form.cleaned_data['date_fin'])
    
    # Pagination
    paginator = Paginator(mouvements, 30)
    page_number = request.GET.get('page')
    mouvements_page = paginator.get_page(page_number)
    
    return render(request, 'stocks/mouvement_list.html', {
        'mouvements': mouvements_page,
        'filter_form': form
    })


@login_required
def entree_create(request):
    """Ajouter une entrée de stock (achat)"""
    if request.method == 'POST':
        form = EntreeStockForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                mouvement = StockService.creer_mouvement(
                    produit_id=form.cleaned_data['produit'].id,
                    type_mouvement='ENTREE',
                    quantite=form.cleaned_data['quantite'],
                    user=request.user,
                    date=form.cleaned_data.get('date'),
                    reference=form.cleaned_data.get('reference', ''),
                    prix_unitaire=form.cleaned_data.get('prix_unitaire'),
                    motif=form.cleaned_data.get('motif', '')
                )
                messages.success(request, f"✅ Entrée de {mouvement.quantite} {mouvement.produit.get_unite_display()} enregistrée.")
                return redirect('stocks:mouvement_list')
            except ValueError as e:
                messages.error(request, f"❌ {str(e)}")
    else:
        form = EntreeStockForm(user=request.user)
    
    return render(request, 'stocks/mouvement_form.html', {
        'form': form,
        'title': 'Ajouter une entrée de stock',
        'type_mouvement': 'ENTREE'
    })


@login_required
def sortie_create(request):
    """Ajouter une sortie de stock (consommation)"""
    if request.method == 'POST':
        form = SortieStockForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                mouvement = StockService.creer_mouvement(
                    produit_id=form.cleaned_data['produit'].id,
                    type_mouvement='SORTIE',
                    quantite=form.cleaned_data['quantite'],
                    user=request.user,
                    date=form.cleaned_data.get('date'),
                    reference=form.cleaned_data.get('reference', ''),
                    motif=form.cleaned_data.get('motif', '')
                )
                messages.success(request, f"✅ Sortie de {mouvement.quantite} {mouvement.produit.get_unite_display()} enregistrée.")
                return redirect('stocks:mouvement_list')
            except ValueError as e:
                messages.error(request, f"❌ {str(e)}")
    else:
        form = SortieStockForm(user=request.user)
    
    return render(request, 'stocks/mouvement_form.html', {
        'form': form,
        'title': 'Ajouter une sortie de stock',
        'type_mouvement': 'SORTIE'
    })


@login_required
def mouvement_delete(request, pk):
    """
    Supprimer un mouvement et compenser son effet sur le stock.
    """
    mouvement = get_object_or_404(
        MouvementStock, 
        pk=pk, 
        produit__ferme=request.user.ferme
    )
    
    if request.method == 'POST':
        with transaction.atomic():
            produit = ProduitStock.objects.select_for_update().get(pk=mouvement.produit_id)

            if mouvement.type == 'ENTREE':
                produit.quantite_actuelle -= mouvement.quantite
            else:
                produit.quantite_actuelle += mouvement.quantite

            if produit.quantite_actuelle < 0:
                messages.error(request, "❌ Suppression impossible : elle rendrait le stock négatif.")
                return redirect('stocks:mouvement_list')

            produit.save(update_fields=['quantite_actuelle', 'updated_at'])
            mouvement.delete()
        
        messages.success(request, f"🗑️ Mouvement supprimé et stock corrigé.")
        return redirect('stocks:mouvement_list')
    
    return render(request, 'stocks/mouvement_confirm_delete.html', {'object': mouvement})
