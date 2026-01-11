"""
AI_Predictor URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('predictor.auth.urls')),
    path('adminpanel/', include('predictor.adminpanel.urls')),
    path('', include('predictor.urls')),
]
