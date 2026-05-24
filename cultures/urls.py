# cultures/urls.py
from django.urls import path
from . import views

app_name = 'cultures'

urlpatterns = [
    # Parcelles
    path('parcelles/', views.parcelle_list, name='parcelle_list'),
    path('parcelles/create/', views.parcelle_create, name='parcelle_create'),
    path('parcelles/<int:pk>/edit/', views.parcelle_update, name='parcelle_update'),
    path('parcelles/<int:pk>/delete/', views.parcelle_delete, name='parcelle_delete'),
    
    # Cultures (liste globale)
    path('cultures/', views.culture_list, name='culture_list'),
    
    # Association Culture ↔ Parcelle
    path('cultures-parcelles/', views.cultureparcelle_list, name='cultureparcelle_list'),
    path('cultures-parcelles/create/', views.cultureparcelle_create, name='cultureparcelle_create'),
    path('cultures-parcelles/<int:pk>/edit/', views.cultureparcelle_update, name='cultureparcelle_update'),
    path('cultures-parcelles/<int:pk>/delete/', views.cultureparcelle_delete, name='cultureparcelle_delete'),
    
    # Activités agricoles
    path('activites/', views.activite_list, name='activite_list'),
    path('activites/create/', views.activite_create, name='activite_create'),
    path('activite_create/', views.activite_create, name='activite_create_legacy'),
    path('activites/<int:pk>/delete/', views.activite_delete, name='activite_delete'),
]
