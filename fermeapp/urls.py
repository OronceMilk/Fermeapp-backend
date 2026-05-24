"""fermeapp URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard:home')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('cheptel/', include('cheptel.urls', namespace='cheptel')),
    path('cultures/', include('cultures.urls', namespace='cultures')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('stocks/', include('stocks.urls', namespace='stocks')),
    path('stock/', include(('stocks.urls', 'stocks'), namespace='stock_alias')),
]
