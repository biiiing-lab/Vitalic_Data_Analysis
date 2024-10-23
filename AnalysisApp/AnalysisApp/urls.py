from . import views
from django.urls import path

urlpatterns = [
    # monthly, weekly, daily = mwd
    path('api/mwd/report', views.transaction_summary, name='transaction_summary'),
]
