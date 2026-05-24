# cultures/views.py - Version corrigée avec sécurité multi-ferme

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Parcelle, Culture, CultureParcelle, ActiviteAgricole
from .forms import ParcelleForm, CultureParcelleForm, ActiviteAgricoleForm


# ==============================
# PARCELLES
# ==============================

@login_required
def parcelle_list(request):
    parcelles = Parcelle.objects.filter(
        ferme=request.user.ferme
    ).annotate(
        cultures_count=Count('cultures_associees')
    )
    return render(request, 'cultures/parcelle_list.html', {'parcelles': parcelles})


@login_required
def parcelle_create(request):
    if request.method == 'POST':
        form = ParcelleForm(request.POST)
        if form.is_valid():
            parcelle = form.save(commit=False)
            parcelle.ferme = request.user.ferme
            parcelle.save()
            messages.success(request, "✅ Parcelle créée avec succès.")
            return redirect('cultures:parcelle_list')
    else:
        form = ParcelleForm()
    
    return render(request, 'cultures/parcelle_form.html', {'form': form, 'title': 'Créer une parcelle'})


@login_required
def parcelle_update(request, pk):
    parcelle = get_object_or_404(Parcelle, pk=pk, ferme=request.user.ferme)
    
    if request.method == 'POST':
        form = ParcelleForm(request.POST, instance=parcelle)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Parcelle mise à jour.")
            return redirect('cultures:parcelle_list')
    else:
        form = ParcelleForm(instance=parcelle)
    
    return render(request, 'cultures/parcelle_form.html', {'form': form, 'title': 'Modifier la parcelle'})


@login_required
def parcelle_delete(request, pk):
    parcelle = get_object_or_404(Parcelle, pk=pk, ferme=request.user.ferme)
    
    if request.method == 'POST':
        parcelle.delete()
        messages.success(request, "🗑️ Parcelle supprimée.")
        return redirect('cultures:parcelle_list')
    
    return render(request, 'cultures/parcelle_confirm_delete.html', {'object': parcelle})


# ==============================
# CULTURES (liste globale - lecture seule)
# ==============================

@login_required
def culture_list(request):
    # Les cultures sont globales, pas filtrées par ferme
    cultures = Culture.objects.all().annotate(
        parcelles_count=Count('parcelles_associees')
    )
    return render(request, 'cultures/culture_list.html', {'cultures': cultures})


# ==============================
# ASSOCIATIONS CULTURE ↔ PARCELLE
# ==============================

@login_required
def cultureparcelle_list(request):
    cultures_parcelles = CultureParcelle.objects.filter(
        parcelle__ferme=request.user.ferme
    ).select_related('parcelle', 'culture').annotate(
        activites_count=Count('activites')
    )
    return render(request, 'cultures/cultureparcelle_list.html', {'cultures_parcelles': cultures_parcelles})


@login_required
def cultureparcelle_create(request):
    if request.method == 'POST':
        form = CultureParcelleForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Culture associée à la parcelle.")
            return redirect('cultures:cultureparcelle_list')
    else:
        form = CultureParcelleForm(user=request.user)
    
    return render(request, 'cultures/cultureparcelle_form.html', {'form': form, 'title': 'Associer une culture'})


@login_required
def cultureparcelle_update(request, pk):
    culture_parcelle = get_object_or_404(
        CultureParcelle, 
        pk=pk, 
        parcelle__ferme=request.user.ferme
    )
    
    if request.method == 'POST':
        form = CultureParcelleForm(request.POST, instance=culture_parcelle, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Association mise à jour.")
            return redirect('cultures:cultureparcelle_list')
    else:
        form = CultureParcelleForm(instance=culture_parcelle, user=request.user)
    
    return render(request, 'cultures/cultureparcelle_form.html', {'form': form, 'title': 'Modifier l\'association'})


@login_required
def cultureparcelle_delete(request, pk):
    culture_parcelle = get_object_or_404(
        CultureParcelle, 
        pk=pk, 
        parcelle__ferme=request.user.ferme
    )
    
    if request.method == 'POST':
        culture_parcelle.delete()
        messages.success(request, "🗑️ Association supprimée.")
        return redirect('cultures:cultureparcelle_list')
    
    return render(request, 'cultures/cultureparcelle_confirm_delete.html', {'object': culture_parcelle})


# ==============================
# ACTIVITÉS AGRICOLES
# ==============================

@login_required
def activite_list(request):
    activites = ActiviteAgricole.objects.filter(
        culture_parcelle__parcelle__ferme=request.user.ferme
    ).select_related(
        'culture_parcelle', 
        'culture_parcelle__culture', 
        'culture_parcelle__parcelle', 
        'operateur'
    )
    return render(request, 'cultures/activite_list.html', {'activites': activites})


@login_required
def activite_create(request):
    if request.method == 'POST':
        form = ActiviteAgricoleForm(request.POST, user=request.user)
        if form.is_valid():
            activite = form.save(commit=False)
            activite.operateur = request.user
            activite.save()
            messages.success(request, "✅ Activité enregistrée.")
            return redirect('cultures:activite_list')
    else:
        form = ActiviteAgricoleForm(user=request.user)
    
    return render(request, 'cultures/activite_form.html', {'form': form, 'title': 'Ajouter une activité'})


@login_required
def activite_delete(request, pk):
    activite = get_object_or_404(
        ActiviteAgricole, 
        pk=pk, 
        culture_parcelle__parcelle__ferme=request.user.ferme
    )
    
    if request.method == 'POST':
        activite.delete()
        messages.success(request, "🗑️ Activité supprimée.")
        return redirect('cultures:activite_list')
    
    return render(request, 'cultures/activite_confirm_delete.html', {'object': activite})