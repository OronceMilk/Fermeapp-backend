# stocks/urls.py
from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('', views.stock_dashboard, name='dashboard'),
    path('partials/aliments/', views.aliments_partial, name='aliments_partial'),
    path('partials/semences/', views.semences_partial, name='semences_partial'),

    # ==============================
    # PRODUITS
    # ==============================
    path('produits/', views.produit_list, name='produit_list'),
    path('produits/create/', views.produit_create, name='produit_create'),
    path('produits/<int:pk>/edit/', views.produit_update, name='produit_update'),
    path('produits/<int:pk>/delete/', views.produit_delete, name='produit_delete'),
    
    # ==============================
    # MOUVEMENTS
    # ==============================
    path('mouvements/', views.mouvement_list, name='mouvement_list'),
    path('mouvements/entree/', views.entree_create, name='entree_create'),
    path('mouvements/sortie/', views.sortie_create, name='sortie_create'),
    path('mouvements/<int:pk>/delete/', views.mouvement_delete, name='mouvement_delete'),
]
