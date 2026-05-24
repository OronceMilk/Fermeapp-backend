# accounts/urls.py
from django.urls import path
from . import views
from django.shortcuts import redirect  # ← Ajouter cette ligne

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 🔥 Redirections vers dashboard unifié
    path('admin-dashboard/', lambda request: redirect('dashboard:home'), name='admin_dashboard'),
    path('employe-dashboard/', lambda request: redirect('dashboard:home'), name='employe_dashboard'),
    
    # Redirection racine
    path('', views.home_redirect, name='home'),
]