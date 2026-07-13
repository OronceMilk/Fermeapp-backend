# dashboard/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.cache import cache
from django.utils import timezone
from .services import (
    get_kpis,
    get_alertes,
    get_production_data,
    get_animaux_par_espece,
    get_recent_activities,
    get_finances,
    get_stock_evolution,
    get_depenses_par_produit,
    get_health_score,
    get_health_status,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vue principale du tableau de bord - V2 avec cache et nouveaux services"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        # 🔥 ERREUR VOLONTAIRE POUR TEST SENTRY
raise Exception("Test Sentry - erreur volontaire")
        context = super().get_context_data(**kwargs)
        context['date_today'] = timezone.now()
        user = self.request.user
        
        # 🔥 CACHE (60 secondes pour éviter les calculs trop fréquents)
        cache_key = f"dashboard_v2_{user.id}_{user.ferme.id}"
        data = cache.get(cache_key)
        
        if not data:
            # Récupérer les KPIs d'abord (nécessaires pour health_score)
            kpis = get_kpis(user)
            
            # Récupérer toutes les données via les services
            data = {
                'kpis': kpis,
                'alertes': get_alertes(user),
                'production_data': get_production_data(user),
                'animaux_par_espece': get_animaux_par_espece(user),
                'activites': get_recent_activities(user),
                'finances': get_finances(user),
                'stock_evolution': get_stock_evolution(user),
                'depenses_par_produit': get_depenses_par_produit(user),
                'health_score': get_health_score(kpis),
                'health_status': get_health_status(get_health_score(kpis)),
            }
            cache.set(cache_key, data, 60)  # 60 secondes
        
        context.update(data)
        return context