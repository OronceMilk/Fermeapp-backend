# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from .forms import CustomAuthenticationForm, InscriptionForm
from .services import inscrire_nouvelle_ferme, EmailDejaUtiliseException


class InscriptionView(FormView):
    template_name = 'accounts/inscription.html'
    form_class = InscriptionForm
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        try:
            user = inscrire_nouvelle_ferme(
                donnees_ferme={
                    'nom': form.cleaned_data['ferme_nom'],
                    'localisation': form.cleaned_data['ferme_localisation'],
                    'email': form.cleaned_data['ferme_email'],
                    'telephone': form.cleaned_data.get('ferme_telephone', ''),
                },
                donnees_admin={
                    'username': form.cleaned_data['admin_username'],
                    'email': form.cleaned_data['admin_email'],
                    'password': form.cleaned_data['admin_password'],
                }
            )
            login(self.request, user)
            messages.success(self.request, "✅ Ferme créée avec succès ! Bienvenue sur FermeApp.")
            return super().form_valid(form)
        except EmailDejaUtiliseException as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except ValidationError as e:
            # Capture toute ValidationError non anticipée (ex: username invalide)
            form.add_error(None, " ".join(e.messages) if hasattr(e, 'messages') else str(e))
            return self.form_invalid(form)


class CustomLoginView(LoginView):
    """Vue de connexion professionnelle avec CBV"""
    template_name = 'accounts/login_v2.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirection intelligente après connexion"""
        return self.request.user.get_dashboard_url()
    
    def get(self, request, *args, **kwargs):
        """Nettoyer les messages flash au chargement de la page de login"""
        # 🔥 Supprimer les messages flash existants avant d'afficher le formulaire
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # vide la session des messages
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Ajout d'un message de bienvenue"""
        response = super().form_valid(form)
        messages.success(self.request, f'Bienvenue {self.request.user.username} !')
        return response
    
    def form_invalid(self, form):
        """Gestion des erreurs"""
        return super().form_invalid(form)


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accounts:login')


@login_required
def admin_dashboard(request):
    """Dashboard ADMIN - Vérification du rôle"""
    if request.user.role != 'ADMIN':
        raise PermissionDenied("Accès réservé aux administrateurs.")
    
    context = {
        'user': request.user,
        'ferme': request.user.ferme,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def employe_dashboard(request):
    """Dashboard EMPLOYE - Vérification du rôle"""
    if request.user.role != 'EMPLOYE':
        raise PermissionDenied("Accès réservé aux employés.")
    
    context = {
        'user': request.user,
        'ferme': request.user.ferme,
    }
    return render(request, 'accounts/employe_dashboard.html', context)


@login_required
def home_redirect(request):
    """Redirection racine via la méthode du modèle"""
    return redirect(request.user.get_dashboard_url())