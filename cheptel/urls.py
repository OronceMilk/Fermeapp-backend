# cheptel/urls.py
from django.urls import path
from .views import (
    AnimalListView,
    AnimalCreateView,
    AnimalUpdateView,
    AnimalDeleteView,
    LotListView,
    LotCreateView,
    LotUpdateView,
    LotDeleteView,
    RapportJournalierListView,
    RapportJournalierCreateView,
    RapportJournalierUpdateView,
    RapportJournalierDeleteView,
    TraitementListView,
    TraitementCreateView,
    TraitementUpdateView,
    TraitementDeleteView,
)

app_name = 'cheptel'  # ← AJOUTE CETTE LIGNE !

# cheptel/urls.py (ajoute dans urlpatterns)

urlpatterns = [
    # URLs existantes des animaux
    path('', AnimalListView.as_view(), name='animal_list'),
    path('add/', AnimalCreateView.as_view(), name='animal_add'),
    path('<int:pk>/edit/', AnimalUpdateView.as_view(), name='animal_edit'),
    path('<int:pk>/delete/', AnimalDeleteView.as_view(), name='animal_delete'),
    
    # 🔥 NOUVELLES URLs pour les lots
    path('lots/', LotListView.as_view(), name='lot_list'),
    path('lots/add/', LotCreateView.as_view(), name='lot_create'),
    path('lots/<int:pk>/edit/', LotUpdateView.as_view(), name='lot_edit'),
    path('lots/<int:pk>/delete/', LotDeleteView.as_view(), name='lot_delete'),

    # 🔥 RAPPORTS JOURNALIERS
    path('rapports/', RapportJournalierListView.as_view(), name='rapport_list'),
    path('rapport_list/', RapportJournalierListView.as_view(), name='rapport_list_legacy'),
    path('rapports/add/', RapportJournalierCreateView.as_view(), name='rapport_add'),
    path('rapports/<int:pk>/edit/', RapportJournalierUpdateView.as_view(), name='rapport_edit'),
    path('rapports/<int:pk>/delete/', RapportJournalierDeleteView.as_view(), name='rapport_delete'),

    # 🔥 TRAITEMENTS SANITAIRES
    path('traitements/', TraitementListView.as_view(), name='traitement_list'),
    path('traitements/add/', TraitementCreateView.as_view(), name='traitement_add'),
    path('traitements/<int:pk>/edit/', TraitementUpdateView.as_view(), name='traitement_edit'),
    path('traitements/<int:pk>/delete/', TraitementDeleteView.as_view(), name='traitement_delete'),
]
