# cheptel/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Avg, Sum
from datetime import date, timedelta
from accounts.decorators import admin_required
from .models import Animal, Espece, LotPondeuses, RapportJournalier, Traitement
from .forms import AnimalForm, LotForm, RapportJournalierForm, TraitementForm


# ==============================
# ANIMAUX
# ==============================
class AnimalListView(LoginRequiredMixin, ListView):
    model = Animal
    template_name = 'cheptel/animal_list.html'
    context_object_name = 'animaux'
    
    def get_queryset(self):
        queryset = Animal.objects.filter(ferme=self.request.user.ferme).select_related('espece', 'lot')

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        espece = self.request.GET.get('espece')
        if espece and espece.isdigit():
            queryset = queryset.filter(espece_id=int(espece))

        lot = self.request.GET.get('lot')
        if lot and lot.isdigit():
            queryset = queryset.filter(lot_id=int(lot))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ferme'] = self.request.user.ferme
        context['especes'] = Espece.objects.all().order_by('nom')
        context['lots'] = LotPondeuses.objects.filter(ferme=self.request.user.ferme).order_by('-date_mise_en_place')

        animaux_ferme = Animal.objects.filter(ferme=self.request.user.ferme)
        context['stats'] = {
            'total': animaux_ferme.count(),
            'actif': animaux_ferme.filter(statut='ACTIF').count(),
            'decede': animaux_ferme.filter(statut='DECEDE').count(),
            'vendu': animaux_ferme.filter(statut='VENDU').count(),
        }

        context['filtres_actifs'] = {
            'statut': self.request.GET.get('statut', ''),
            'espece': self.request.GET.get('espece', ''),
            'lot': self.request.GET.get('lot', ''),
        }
        return context


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'cheptel/animal_form.html'
    success_url = reverse_lazy('cheptel:animal_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.ferme = self.request.user.ferme
        form.instance.createur = self.request.user
        messages.success(self.request, "✅ Animal ajouté avec succès !")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un animal'
        return context


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'cheptel/animal_form.html'
    success_url = reverse_lazy('cheptel:animal_list')
    
    def get_queryset(self):
        return Animal.objects.filter(ferme=self.request.user.ferme)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # 🔥 Sauvegarder sans commit pour préserver createur
        instance = form.save(commit=False)
        
        # Récupérer et préserver le créateur original si l'animal existe
        if instance.pk:
            original_animal = Animal.objects.get(pk=instance.pk)
            instance.createur = original_animal.createur
        else:
            instance.createur = self.request.user
        
        # Sauvegarder l'animal avec le createur préservé
        instance.save()
        messages.success(self.request, "✏️ Animal modifié avec succès !")
        return redirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un animal'
        return context


class AnimalDeleteView(LoginRequiredMixin, DeleteView):
    model = Animal
    template_name = 'cheptel/animal_confirm_delete.html'
    success_url = reverse_lazy('cheptel:animal_list')
    
    def get_queryset(self):
        return Animal.objects.filter(ferme=self.request.user.ferme)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "🗑️ Animal supprimé avec succès !")
        return super().delete(request, *args, **kwargs)


# ==============================
# LOTS
# ==============================
class LotListView(LoginRequiredMixin, ListView):
    model = LotPondeuses
    template_name = 'cheptel/lot_list.html'
    context_object_name = 'lots'
    ordering = ['-date_mise_en_place']
    
    def get_queryset(self):
        return LotPondeuses.objects.filter(ferme=self.request.user.ferme)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for lot in context['lots']:
            lot.nb_animaux = Animal.objects.filter(lot=lot).count()
        context['total_lots'] = LotPondeuses.objects.filter(ferme=self.request.user.ferme).count()
        context['total_sujets'] = sum(lot.nombre_sujets for lot in LotPondeuses.objects.filter(ferme=self.request.user.ferme))
        return context


class LotCreateView(LoginRequiredMixin, CreateView):
    model = LotPondeuses
    form_class = LotForm
    template_name = 'cheptel/lot_form.html'
    success_url = reverse_lazy('cheptel:lot_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.ferme = self.request.user.ferme
        form.instance.createur = self.request.user
        messages.success(self.request, f"✅ Lot '{form.instance.nom}' créé avec succès !")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer un nouveau lot'
        context['button_text'] = 'Créer le lot'
        return context


class LotUpdateView(LoginRequiredMixin, UpdateView):
    model = LotPondeuses
    form_class = LotForm
    template_name = 'cheptel/lot_form.html'
    success_url = reverse_lazy('cheptel:lot_list')
    
    def get_queryset(self):
        return LotPondeuses.objects.filter(ferme=self.request.user.ferme)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"✏️ Lot '{form.instance.nom}' modifié avec succès !")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le lot'
        context['button_text'] = 'Enregistrer les modifications'
        return context


class LotDeleteView(LoginRequiredMixin, DeleteView):
    model = LotPondeuses
    template_name = 'cheptel/lot_confirm_delete.html'
    success_url = reverse_lazy('cheptel:lot_list')
    
    def get_queryset(self):
        return LotPondeuses.objects.filter(ferme=self.request.user.ferme)
    
    def delete(self, request, *args, **kwargs):
        lot = self.get_object()
        messages.success(self.request, f"🗑️ Lot '{lot.nom}' supprimé avec succès !")
        return super().delete(request, *args, **kwargs)


# ==============================
# RAPPORTS JOURNALIERS
# ==============================
class RapportJournalierListView(LoginRequiredMixin, ListView):
    """Liste des rapports journaliers de la ferme"""
    model = RapportJournalier
    template_name = 'cheptel/rapport_list.html'
    context_object_name = 'rapports'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = RapportJournalier.objects.filter(
            ferme=self.request.user.ferme
        ).order_by('-date')
        
        annee = self.request.GET.get('annee')
        mois = self.request.GET.get('mois')
        
        if annee and annee.isdigit():
            queryset = queryset.filter(date__year=int(annee))
        if mois and mois.isdigit():
            queryset = queryset.filter(date__month=int(mois))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        rapports_mois = self.get_queryset().filter(
            date__year=date.today().year,
            date__month=date.today().month
        )
        
        context['total_morts_mois'] = rapports_mois.aggregate(Sum('nombre_morts'))['nombre_morts__sum'] or 0
        context['total_oeufs_mois'] = rapports_mois.aggregate(Sum('oeufs_pondus'))['oeufs_pondus__sum'] or 0
        context['moyenne_aliment'] = rapports_mois.aggregate(Avg('aliment_kg'))['aliment_kg__avg'] or 0
        
        context['annees_disponibles'] = RapportJournalier.objects.filter(
            ferme=self.request.user.ferme
        ).dates('date', 'year', order='DESC')
        
        return context


class RapportJournalierCreateView(LoginRequiredMixin, CreateView):
    model = RapportJournalier
    form_class = RapportJournalierForm
    template_name = 'cheptel/rapport_form.html'
    success_url = reverse_lazy('cheptel:rapport_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ferme'] = self.request.user.ferme
        return kwargs
    
    def form_valid(self, form):
        form.instance.ferme = self.request.user.ferme
        form.instance.createur = self.request.user
        try:
            response = super().form_valid(form)
        except ValidationError as exc:
            if hasattr(exc, 'message_dict'):
                for field, errors in exc.message_dict.items():
                    for error in errors:
                        if field == '__all__':
                            form.add_error(None, error)
                        else:
                            form.add_error(field, error)
            else:
                form.add_error(None, exc.message)
            return self.form_invalid(form)

        messages.success(self.request, f"✅ Rapport du {form.instance.date.strftime('%d/%m/%Y')} enregistré !")
        return response

    def form_invalid(self, form):
        """Capture les erreurs de validation et les affiche à l'utilisateur"""
        if '__all__' in form.errors:
            messages.error(self.request, form.errors['__all__'][0])
        else:
            for field, errors in form.errors.items():
                messages.error(self.request, f"{field}: {errors[0]}")

        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau rapport journalier'
        return context


class RapportJournalierUpdateView(LoginRequiredMixin, UpdateView):
    model = RapportJournalier
    form_class = RapportJournalierForm
    template_name = 'cheptel/rapport_form.html'
    success_url = reverse_lazy('cheptel:rapport_list')
    
    def get_queryset(self):
        return RapportJournalier.objects.filter(ferme=self.request.user.ferme)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ferme'] = self.request.user.ferme
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"✏️ Rapport du {form.instance.date.strftime('%d/%m/%Y')} modifié !")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le rapport'
        return context


class RapportJournalierDeleteView(LoginRequiredMixin, DeleteView):
    model = RapportJournalier
    template_name = 'cheptel/rapport_confirm_delete.html'
    success_url = reverse_lazy('cheptel:rapport_list')
    
    def get_queryset(self):
        return RapportJournalier.objects.filter(ferme=self.request.user.ferme)
    
    def delete(self, request, *args, **kwargs):
        rapport = self.get_object()
        messages.success(request, f"🗑️ Rapport du {rapport.date.strftime('%d/%m/%Y')} supprimé !")
        return super().delete(request, *args, **kwargs)


# ==============================
# TRAITEMENTS SANITAIRES
# ==============================
class TraitementListView(LoginRequiredMixin, ListView):
    """Liste des traitements avec filtres"""
    model = Traitement
    template_name = 'cheptel/traitement_list.html'
    context_object_name = 'traitements'
    paginate_by = 20
    
    def get_queryset(self):
        # Récupérer tous les animaux de la ferme de l'utilisateur
        animaux_ferme = Animal.objects.filter(ferme=self.request.user.ferme)
        
        # Filtrer les traitements par ces animaux
        queryset = Traitement.objects.filter(
            animal__in=animaux_ferme
        ).select_related('animal', 'produit', 'operateur').order_by('-date')
        
        # Filtre par type
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Filtre par animal
        animal_filter = self.request.GET.get('animal')
        if animal_filter and animal_filter.isdigit():
            queryset = queryset.filter(animal_id=int(animal_filter))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Animaux pour le filtre
        context['animaux'] = Animal.objects.filter(
            ferme=self.request.user.ferme,
            statut='ACTIF'
        ).order_by('identifiant')
        
        # Alertes : rappels de vaccins dans les 7 jours
        today = date.today()
        animaux_ferme = Animal.objects.filter(ferme=self.request.user.ferme)
        
        context['alertes_rappel'] = Traitement.objects.filter(
            animal__in=animaux_ferme,
            rappel_le__isnull=False,
            rappel_le__gte=today,
            rappel_le__lte=today + timedelta(days=7)
        ).select_related('animal')
        
        # Statistiques
        context['total_traitements'] = self.get_queryset().count()
        context['vaccins_mois'] = self.get_queryset().filter(
            type='VACCIN',
            date__year=today.year,
            date__month=today.month
        ).count()
        
        context['today'] = today
        
        return context


class TraitementCreateView(LoginRequiredMixin, CreateView):
    model = Traitement
    form_class = TraitementForm
    template_name = 'cheptel/traitement_form.html'
    success_url = reverse_lazy('cheptel:traitement_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.ferme = self.request.user.ferme
        form.instance.operateur = self.request.user
        messages.success(self.request, f"✅ {form.instance.get_type_display()} enregistré pour {form.instance.animal.identifiant}")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un traitement'
        return context


class TraitementUpdateView(LoginRequiredMixin, UpdateView):
    model = Traitement
    form_class = TraitementForm
    template_name = 'cheptel/traitement_form.html'
    success_url = reverse_lazy('cheptel:traitement_list')
    
    def get_queryset(self):
        return Traitement.objects.filter(animal__ferme=self.request.user.ferme)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"✏️ {form.instance.get_type_display()} modifié")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le traitement'
        return context


class TraitementDeleteView(LoginRequiredMixin, DeleteView):
    model = Traitement
    template_name = 'cheptel/traitement_confirm_delete.html'
    success_url = reverse_lazy('cheptel:traitement_list')
    
    def get_queryset(self):
        return Traitement.objects.filter(animal__ferme=self.request.user.ferme)
    
    def delete(self, request, *args, **kwargs):
        traitement = self.get_object()
        messages.success(self.request, f"🗑️ {traitement.get_type_display()} supprimé")
        return super().delete(request, *args, **kwargs)