# dashboard/services/__init__.py
from .kpi_service import get_kpis
from .alert_service import get_alertes
from .stats_service import (
    get_production_data,
    get_animaux_par_espece,
    get_stock_evolution,
    get_depenses_par_produit
)
from .activity_service import get_recent_activities
from .finance_service import get_finances
from .health_service import get_health_score, get_health_status

__all__ = [
    'get_kpis',
    'get_alertes',
    'get_production_data',
    'get_animaux_par_espece',
    'get_stock_evolution',
    'get_depenses_par_produit',
    'get_recent_activities',
    'get_finances',
    'get_health_score',
    'get_health_status',
]