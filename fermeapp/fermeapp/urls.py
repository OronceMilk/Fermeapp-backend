from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('cheptel/', views.animal_list, name='animal_list'),
    path('cheptel/add/', views.animal_form, name='animal_add'),
    path('cheptel/ajouter/', views.animal_form, name='animal_form'),
    path('cheptel/<int:pk>/edit/', views.animal_form, name='animal_edit_legacy'),
    path('cheptel/<int:pk>/modifier/', views.animal_form, name='animal_edit'),
    path('cheptel/<int:pk>/delete/', views.animal_delete, name='animal_delete_legacy'),
    path('cheptel/<int:pk>/supprimer/', views.animal_delete, name='animal_delete'),
    path('cheptel/lots/', views.lot_list, name='lot_list'),
    path('cheptel/comptages/', views.comptage_list, name='comptage_list'),
    path('cheptel/comptages/add/', views.comptage_add, name='comptage_add'),
    path('cheptel/traitements/', views.traitement_list, name='traitement_list'),
    path('parametres/', views.parametres, name='parametres'),
    # HTMX endpoints
    path('api/cheptel/filtrer/', views.filter_animals, name='filter_animals'),
    path('api/traitements/', views.traitement_list, name='traitement_list_api'),
]
