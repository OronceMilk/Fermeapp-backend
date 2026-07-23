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
from .services import (
    get_animaux_ferme, get_stats_cheptel, get_lots_avec_comptage,
    creer_animal, mettre_a_jour_animal,
    get_traitements_ferme, get_alertes_rappel, creer_traitement,
)
from .services import (
    get_animaux_ferme, get_stats_cheptel, get_lots_avec_comptage,
    creer_animal, mettre_a_jour_animal,
    get_traitements_ferme, get_alertes_rappel, creer_traitement,
    get_rapports_ferme, get_stats_rapports_mois, creer_lot,
)

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
        animal = creer_animal(form, ferme=self.request.user.ferme, createur=self.request.user)
        self.object = animal
        messages.success(self.request, "✅ Animal ajouté avec succès !")
        return redirect(self.get_success_url())
    
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
        mettre_a_jour_animal(form, self.request.user)
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
        return get_lots_avec_comptage(self.request.user.ferme)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_lots'] = context['lots'].count()
        context['total_sujets'] = sum(lot.nombre_sujets for lot in context['lots'])
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
        creer_lot(form, ferme=self.request.user.ferme, createur=self.request.user)
        messages.success(self.request, f"✅ Lot '{form.instance.nom}' créé avec succès !")
        return redirect(self.get_success_url())
    
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
        annee = self.request.GET.get('annee')
        mois = self.request.GET.get('mois')
        return get_rapports_ferme(
            ferme=self.request.user.ferme,
            annee=int(annee) if annee and annee.isdigit() else None,
            mois=int(mois) if mois and mois.isdigit() else None,
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update(get_stats_rapports_mois(self.request.user.ferme))
        
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
        animal_filter = self.request.GET.get('animal')
        return get_traitements_ferme(
            ferme=self.request.user.ferme,
            type_filtre=self.request.GET.get('type') or None,
            animal_id=int(animal_filter) if animal_filter and animal_filter.isdigit() else None,
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Animaux pour le filtre
        context['animaux'] = Animal.objects.filter(
            ferme=self.request.user.ferme,
            statut='ACTIF'
        ).order_by('identifiant')
        
        context['alertes_rappel'] = get_alertes_rappel(self.request.user.ferme)
        
        today = date.today()
        
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
        creer_traitement(form, ferme=self.request.user.ferme, operateur=self.request.user)
        messages.success(self.request, f"✅ {form.instance.get_type_display()} enregistré pour {form.instance.animal.identifiant}")
        return redirect(self.get_success_url())
    
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