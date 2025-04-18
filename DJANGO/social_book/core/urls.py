from django.urls import path
from . import views

urlpatterns = [
    path('', views.financeadvisor_view, name='financeadvisor'),
    path('get_advice/', views.get_financial_advice, name='get_financial_advice'),
]
