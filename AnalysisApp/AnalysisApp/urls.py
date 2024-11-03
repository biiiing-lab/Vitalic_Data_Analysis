from . import views
from django.urls import path

urlpatterns = [
    # monthly, weekly, daily = mwd
    path('api/report/mwd', views.transaction_summary, name='transaction_summary'),
    path('api/report/fixed', views.fixed_expenses, name='fixed_expenses'),
    path('api/report/calendar', views.calendar_return, name='calendar_return'),
    path('api/report/monthly', views.monthly_summary, name='monthly_summary'),
    path('api/report/calendar/all', views.monthly_return, name='quarter_summary'),
]
