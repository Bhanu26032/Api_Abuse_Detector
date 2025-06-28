from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('logs/', views.logs_view, name='logs'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('login/sso/', views.sso_login_view, name='sso_login'),
    path('proxy/<path:path>/', views.proxy_to_fastapi),
    path('proxy/', views.proxy_to_fastapi),
]   