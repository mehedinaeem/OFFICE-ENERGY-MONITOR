from rest_framework import serializers

from .models import Alert, Device, Room


class DeviceSerializer(serializers.ModelSerializer):
    room = serializers.SlugRelatedField(read_only=True, slug_field='slug')

    class Meta:
        model = Device
        fields = (
            'id',
            'room',
            'name',
            'device_type',
            'status',
            'wattage',
            'current_power',
            'last_changed',
            'turned_on_at',
        )


class RoomSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'devices',
        )


class AlertSerializer(serializers.ModelSerializer):
    room = serializers.SlugRelatedField(read_only=True, slug_field='slug')

    class Meta:
        model = Alert
        fields = (
            'id',
            'room',
            'message',
            'severity',
            'created_at',
            'resolved',
        )
