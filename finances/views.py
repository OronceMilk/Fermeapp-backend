from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Transaction
from .forms import TransactionForm
from .services import get_transactions_ferme, creer_transaction
from dashboard.services.finance_service import get_finances_mois, get_evolution_annuelle


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finances/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        type_filtre = self.request.GET.get('type')
        return get_transactions_ferme(self.request.user.ferme, type_filtre=type_filtre or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finances_mois'] = get_finances_mois(self.request.user)
        context['evolution_annuelle'] = get_evolution_annuelle(self.request.user)
        context['filtre_type'] = self.request.GET.get('type', '')
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finances/transaction_form.html'
    success_url = reverse_lazy('finances:liste')

    def form_valid(self, form):
        transaction = creer_transaction(
            ferme=self.request.user.ferme,
            createur=self.request.user,
            type=form.cleaned_data['type'],
            categorie=form.cleaned_data['categorie'],
            montant=form.cleaned_data['montant'],
            date=form.cleaned_data['date'],
            commentaire=form.cleaned_data.get('commentaire', ''),
        )
        self.object = transaction
        messages.success(self.request, "✅ Transaction enregistrée avec succès !")
        return redirect(self.get_success_url())