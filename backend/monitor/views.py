from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Alert, Device, Room
from .serializers import AlertSerializer, DeviceSerializer, RoomSerializer


OFFICE_START_HOUR = 9
OFFICE_END_HOUR = 17
POWER_DANGER_THRESHOLD = 400
ASSUMED_COST_PER_KWH = 10
OFFICE_DAY_HOURS = 8


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


def _rooms_queryset():
    return Room.objects.prefetch_related(
        Prefetch('devices', queryset=Device.objects.order_by('device_type', 'name'))
    ).order_by('name')


def _is_outside_office_hours():
    current_time = timezone.localtime().time()
    return (
        current_time.hour < OFFICE_START_HOUR
        or current_time.hour >= OFFICE_END_HOUR
    )


def _room_usage(rooms):
    usage_rows = []

    for room in rooms:
        devices = list(room.devices.all())
        devices_on = [device for device in devices if device.status == Device.Status.ON]

        usage_rows.append({
            'room': room.name,
            'slug': room.slug,
            'power': sum(device.current_power for device in devices),
            'devices_on': len(devices_on),
            'total_devices': len(devices),
        })

    return usage_rows


def _room_status_summary(room):
    devices = list(room.devices.all())
    fans = [device for device in devices if device.device_type == Device.DeviceType.FAN]
    lights = [
        device for device in devices
        if device.device_type == Device.DeviceType.LIGHT
    ]

    return {
        'name': room.name,
        'slug': room.slug,
        'fans_on': sum(1 for device in fans if device.status == Device.Status.ON),
        'lights_on': sum(
            1 for device in lights if device.status == Device.Status.ON
        ),
        'total_fans': len(fans),
        'total_lights': len(lights),
        'power': sum(device.current_power for device in devices),
    }


def _usage_estimates(total_power):
    estimated_hourly_kwh = total_power / 1000
    estimated_daily_kwh = estimated_hourly_kwh * OFFICE_DAY_HOURS
    estimated_daily_cost = estimated_daily_kwh * ASSUMED_COST_PER_KWH

    return {
        'estimated_hourly_kwh': round(estimated_hourly_kwh, 3),
        'estimated_daily_kwh': round(estimated_daily_kwh, 3),
        'estimated_daily_cost': round(estimated_daily_cost, 2),
        'assumed_cost_per_kwh': ASSUMED_COST_PER_KWH,
        'assumption_label': 'Assumed demo rate: 10 BDT/kWh',
    }


def _refresh_alerts(rooms, total_power):
    Alert.objects.filter(resolved=False).delete()

    new_alerts = []

    if _is_outside_office_hours():
        for room in rooms:
            devices_on = [
                device for device in room.devices.all()
                if device.status == Device.Status.ON
            ]

            if devices_on:
                new_alerts.append(Alert(
                    room=room,
                    message=(
                        f'{len(devices_on)} device(s) left ON in '
                        f'{room.name} outside office hours.'
                    ),
                    severity=Alert.Severity.WARNING,
                ))

    if total_power > POWER_DANGER_THRESHOLD:
        new_alerts.append(Alert(
            message=(
                f'Total power is {total_power}W, above the '
                f'{POWER_DANGER_THRESHOLD}W limit.'
            ),
            severity=Alert.Severity.DANGER,
        ))

    if new_alerts:
        Alert.objects.bulk_create(new_alerts)


def _snapshot_data(refresh_alerts=False):
    rooms = list(_rooms_queryset())
    devices = list(Device.objects.select_related('room').order_by('room__name', 'name'))
    total_power = sum(device.current_power for device in devices)

    if refresh_alerts:
        _refresh_alerts(rooms, total_power)

    active_alerts = Alert.objects.filter(resolved=False).select_related('room').order_by(
        '-created_at'
    )
    usage_rows = _room_usage(rooms)

    return {
        'updated_at': timezone.now(),
        'summary': {
            'total_rooms': len(rooms),
            'total_devices': len(devices),
            'devices_on': sum(
                1 for device in devices if device.status == Device.Status.ON
            ),
            'total_power': total_power,
            'active_alerts': active_alerts.count(),
        },
        'usage': {
            'total_power': total_power,
            **_usage_estimates(total_power),
            'room_usage': usage_rows,
        },
        'rooms': RoomSerializer(rooms, many=True).data,
        'alerts': AlertSerializer(active_alerts, many=True).data,
    }


@api_view(['GET'])
def snapshot(request):
    return Response(_snapshot_data(refresh_alerts=True))


@api_view(['GET'])
def devices(request):
    queryset = Device.objects.select_related('room').order_by('room__name', 'name')
    return Response(DeviceSerializer(queryset, many=True).data)


@api_view(['GET'])
def status_summary(request):
    rooms = list(_rooms_queryset())
    room_summaries = [_room_status_summary(room) for room in rooms]

    return Response({
        'rooms': room_summaries,
        'total_power': sum(room['power'] for room in room_summaries),
        'devices_on': sum(
            room['fans_on'] + room['lights_on'] for room in room_summaries
        ),
        'active_alerts': Alert.objects.filter(resolved=False).count(),
    })


@api_view(['POST'])
def toggle_device(request, device_id):
    device = get_object_or_404(Device.objects.select_related('room'), id=device_id)
    new_status = (
        Device.Status.OFF
        if device.status == Device.Status.ON
        else Device.Status.ON
    )

    device.set_status(new_status)
    device.save(update_fields=[
        'status',
        'current_power',
        'last_changed',
        'turned_on_at',
    ])

    return Response(DeviceSerializer(device).data)


@api_view(['GET'])
def usage(request):
    rooms = list(_rooms_queryset())
    usage_rows = _room_usage(rooms)
    total_power = sum(row['power'] for row in usage_rows)

    return Response({
        'total_power': total_power,
        **_usage_estimates(total_power),
        'room_usage': usage_rows,
    })


@api_view(['GET'])
def alerts(request):
    queryset = Alert.objects.filter(resolved=False).select_related('room').order_by(
        '-created_at'
    )
    alerts_data = AlertSerializer(queryset, many=True).data

    return Response({
        'active_alerts': len(alerts_data),
        'alerts': alerts_data,
    })


@api_view(['GET'])
def room_detail(request, slug):
    room = get_object_or_404(_rooms_queryset(), slug=slug)
    room_data = RoomSerializer(room).data

    return Response({
        **room_data,
        'summary': _room_status_summary(room),
    })
