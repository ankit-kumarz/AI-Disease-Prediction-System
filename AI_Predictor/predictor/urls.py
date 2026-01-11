"""
URL Configuration for predictor app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('diabetes/', views.disease_form_view, {'disease': 'diabetes'}, name='diabetes'),
    path('heart/', views.disease_form_view, {'disease': 'heart'}, name='heart'),
    path('breast/', views.disease_form_view, {'disease': 'breast'}, name='breast'),
    path('result/<int:record_id>/', views.result_view, name='result'),
    path('report/<int:record_id>/', views.report_view, name='report'),
    path('history/', views.history_view, name='history'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/user/history/', views.api_user_history, name='api_user_history'),
]
