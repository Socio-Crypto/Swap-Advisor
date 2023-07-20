from django.urls import path
from .views import DashboardView, LandingView,Cancel,find_dex

urlpatterns = [
    path('dashboard/<network>/<token_in>/<token_out>/<time>/<dexValue>', DashboardView.as_view(), name='dashboard'),
    path('', LandingView.as_view(), name='landing'),
    path('find_dex/', find_dex, name='find_dex'),
    path('cancel/', Cancel.as_view(), name='cancel'),
]
