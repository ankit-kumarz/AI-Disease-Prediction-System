"""
URL configuration for admin panel.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='admin_dashboard'),
    path('users/', views.users_view, name='admin_users'),
    path('predictions/', views.predictions_view, name='admin_predictions'),
    path('predictions/export/', views.export_predictions_csv, name='admin_export_csv'),
    path('analytics/', views.analytics_view, name='admin_analytics'),
]
