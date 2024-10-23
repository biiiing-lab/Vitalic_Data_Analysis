from . import views
from django.urls import path

urlpatterns = [
    # monthly, weekly, daily = mwd
    path('api/report/mwd', views.transaction_summary, name='transaction_summary'),
    path('api/report/fixed', views.fixed_expenses, name='fixed_expenses'),
]
