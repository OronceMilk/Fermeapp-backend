from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
import json
from .models import Animal, Traitement
from .forms import AnimalForm, LoginForm


def login_view(request):
    """Vue de connexion"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard(request):
    """Vue du dashboard"""
    total_animals = Animal.objects.count()
    active_animals = Animal.objects.filter(statut='actif').count()
    sick_animals = Animal.objects.filter(statut='malade').count()
    lots_count = Animal.objects.exclude(lot='').values('lot').distinct().count()
    total_traitements = Traitement.objects.count()
    composition = list(
        Animal.objects.values('espece')
        .annotate(total=Count('id'))
        .order_by('espece')
    )
    espece_labels = [dict(Animal.ESPECE_CHOICES).get(item['espece'], item['espece']) for item in composition]
    espece_values = [item['total'] for item in composition]

    context = {
        'date_today': timezone.localdate(),
        'kpis': [
            {'label': 'Total animaux', 'value': total_animals, 'hint': 'Cheptel enregistré', 'tone': 'navy'},
            {'label': 'Animaux actifs', 'value': active_animals, 'hint': 'Sous surveillance', 'tone': 'green'},
            {'label': 'Lots suivis', 'value': lots_count, 'hint': 'Groupes renseignés', 'tone': 'blue'},
            {'label': 'Traitements', 'value': total_traitements, 'hint': 'Historique sanitaire', 'tone': 'orange'},
            {'label': 'Alertes santé', 'value': sick_animals, 'hint': 'Animaux malades', 'tone': 'red'},
            {'label': 'Comptages', 'value': 0, 'hint': 'Module prêt à connecter', 'tone': 'slate'},
        ],
        'production_labels': json.dumps(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']),
        'production_values': json.dumps([0, 0, 0, 0, 0, 0, 0]),
        'species_labels': json.dumps(espece_labels),
        'species_values': json.dumps(espece_values),
        'alertes': Traitement.objects.select_related('animal').order_by('-date')[:4],
        'activites': Animal.objects.order_by('-date_creation')[:5],
    }
    if request.headers.get('HX-Request'):
        return render(request, 'dashboard/dashboard_partial.html', context)
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def animal_list(request):
    """Liste des animaux avec filtres"""
    animaux = Animal.objects.all().order_by('-date_creation')

    # Appliquer les filtres
    statut = request.GET.get('statut')
    if statut:
        animaux = animaux.filter(statut=statut)

    espece = request.GET.get('espece')
    if espece:
        animaux = animaux.filter(espece=espece)

    lot = request.GET.get('lot')
    if lot:
        animaux = animaux.filter(lot=lot)

    recherche = request.GET.get('recherche')
    if recherche:
        animaux = animaux.filter(
            Q(nom__icontains=recherche) |
            Q(numero_identification__icontains=recherche)
        )

    # Pagination
    paginator = Paginator(animaux, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'animaux': page_obj,
        'statuts': Animal.STATUT_CHOICES,
        'especes': Animal.ESPECE_CHOICES,
        'lots': Animal.objects.exclude(lot='').values_list('lot', flat=True).distinct().order_by('lot'),
    }

    # Si c'est une requête HTMX, retourner seulement le partial
    if request.headers.get('HX-Request'):
        return render(request, 'cheptel/partials/animal_table.html', context)

    return render(request, 'cheptel/animal_list.html', context)


@login_required
def animal_form(request, pk=None):
    """Formulaire d'ajout/modification d'animal"""
    animal = None
    if pk:
        animal = get_object_or_404(Animal, pk=pk)

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            animal = form.save()
            if not request.headers.get('HX-Request'):
                messages.success(request, f'Animal "{animal.nom}" {"modifié" if pk else "créé"}')
                return redirect('animal_list')
            response = HttpResponse()
            response['HX-Toast'] = f'Animal "{animal.nom}" {"modifié" if pk else "créé"} ✅'
            response['HX-Toast-Type'] = 'success'
            response['HX-Redirect'] = reverse('animal_list')
            return response
        else:
            # Erreurs de formulaire
            response = render(request, 'cheptel/animal_form.html', {'form': form, 'animal': animal})
            response['HX-Toast'] = 'Erreur dans le formulaire ❌'
            response['HX-Toast-Type'] = 'error'
            return response
    else:
        form = AnimalForm(instance=animal)

    return render(request, 'cheptel/animal_form.html', {'form': form, 'animal': animal})


@login_required
def animal_delete(request, pk):
    """Suppression d'un animal"""
    animal = get_object_or_404(Animal, pk=pk)
    if request.method == 'POST':
        nom = animal.nom
        animal.delete()
        animaux = Animal.objects.all().order_by('-date_creation')
        paginator = Paginator(animaux, 10)
        response = render(request, 'cheptel/partials/animal_table.html', {
            'animaux': paginator.get_page(request.GET.get('page')),
        })
        response['HX-Toast'] = f'Animal "{nom}" supprimé ✅'
        response['HX-Toast-Type'] = 'success'
        return response
    return HttpResponse(status=405)


@login_required
def filter_animals(request):
    """Endpoint HTMX pour filtrer les animaux"""
    return animal_list(request)


@login_required
def lot_list(request):
    """Vue synthétique des lots existants."""
    lots = (
        Animal.objects.exclude(lot='')
        .values('lot')
        .annotate(total=Count('id'))
        .order_by('lot')
    )
    return render(request, 'cheptel/lot_list.html', {'lots': lots})


@login_required
def comptage_list(request):
    """Page de comptage des productions."""
    lots = (
        Animal.objects.exclude(lot='')
        .values('lot')
        .annotate(total=Count('id'))
        .order_by('lot')
    )
    return render(request, 'cheptel/comptages.html', {'lots': lots, 'comptages': []})


@login_required
def comptage_add(request):
    """Endpoint HTMX temporaire pour le module comptage."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    response = render(request, 'cheptel/comptage_table.html', {'comptages': []})
    response['HX-Toast'] = "Module comptage prêt côté interface, modèle de données à brancher."
    response['HX-Toast-Type'] = 'info'
    return response


@login_required
def parametres(request):
    """Page des paramètres."""
    return render(request, 'Parametres/parametres.html')


@login_required
def traitement_list(request):
    """Liste des traitements"""
    traitements = Traitement.objects.all().order_by('-date')

    # Filtres
    type_traitement = request.GET.get('type')
    if type_traitement:
        traitements = traitements.filter(type=type_traitement)

    animal_nom = request.GET.get('animal')
    if animal_nom:
        traitements = traitements.filter(animal__nom__icontains=animal_nom)

    periode = request.GET.get('periode')
    if periode:
        from datetime import datetime, timedelta
        if periode == '7j':
            date_limit = datetime.now() - timedelta(days=7)
        elif periode == '30j':
            date_limit = datetime.now() - timedelta(days=30)
        elif periode == '90j':
            date_limit = datetime.now() - timedelta(days=90)
        traitements = traitements.filter(date__gte=date_limit)

    context = {
        'traitements': traitements,
        'types_traitement': Traitement.TYPE_CHOICES,
    }

    # Si c'est une requête HTMX, retourner seulement le partial
    if request.headers.get('HX-Request'):
        return render(request, 'cheptel/partials/traitement_timeline.html', context)

    return render(request, 'cheptel/traitement_list.html', context)
