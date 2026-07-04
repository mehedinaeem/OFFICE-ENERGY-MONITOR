from django.urls import path

from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('snapshot/', views.snapshot, name='snapshot'),
    path('status-summary/', views.status_summary, name='status-summary'),
    path('devices/', views.devices, name='devices'),
    path('devices/<int:device_id>/toggle/', views.toggle_device, name='toggle-device'),
    path('usage/', views.usage, name='usage'),
    path('alerts/', views.alerts, name='alerts'),
    path('rooms/<slug:slug>/', views.room_detail, name='room-detail'),
]
