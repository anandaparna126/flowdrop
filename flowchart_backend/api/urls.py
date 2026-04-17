from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', views.login),
    path('auth/logout/', views.logout),
    path('auth/me/', views.me),
    path('charts/', views.charts),
    path('charts/<uuid:chart_id>/', views.chart_detail),
    path('charts/<uuid:chart_id>/share/', views.share_chart),
    path('share/<str:share_token>/', views.access_shared),
    path('users/search/', views.search_users),
]
