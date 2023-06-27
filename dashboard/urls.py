from django.urls import path
from .views import DashboardView, LandingView,find_dex

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('landing', LandingView.as_view(), name='landing'),
    path('find_dex/', find_dex, name='find_dex'),
]
