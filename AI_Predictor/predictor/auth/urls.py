"""
URL configuration for authentication module.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='auth_login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('signup/', views.signup_view, name='auth_signup'),
    path('logout/', views.logout_view, name='auth_logout'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),
]
