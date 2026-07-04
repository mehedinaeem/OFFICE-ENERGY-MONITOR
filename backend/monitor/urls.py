from django.urls import path

from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('snapshot/', views.snapshot, name='snapshot'),
    path('devices/', views.devices, name='devices'),
    path('usage/', views.usage, name='usage'),
    path('alerts/', views.alerts, name='alerts'),
    path('rooms/<slug:slug>/', views.room_detail, name='room-detail'),
]
