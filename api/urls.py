"""
URL configuration for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('ask-question/', views.ask_question, name='ask-question'),
    path('query-history/', views.query_history, name='query-history'),
    path('clear-cache/', views.clear_cache, name='clear-cache'),
    path('stats/', views.system_stats, name='stats'),
]
