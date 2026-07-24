from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='liste'),
    path('nouvelle/', views.TransactionCreateView.as_view(), name='creer'),
]