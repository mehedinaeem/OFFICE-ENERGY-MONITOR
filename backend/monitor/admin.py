from django.contrib import admin
from .models import Alert, Device, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'room',
        'device_type',
        'status',
        'wattage',
        'current_power',
        'last_changed',
    )
    list_filter = ('room', 'device_type', 'status')
    search_fields = ('name', 'room__name')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('message', 'room', 'severity', 'created_at', 'resolved')
    list_filter = ('severity', 'resolved', 'room')
    search_fields = ('message', 'room__name')
