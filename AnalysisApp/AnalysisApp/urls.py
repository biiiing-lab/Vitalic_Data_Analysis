from . import views
from django.urls import path

urlpatterns = [
    path('api/summary/', views.transaction_summary, name='transaction_summary'),
]
