from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Device, Room


class SeedDevicesCommandTests(TestCase):
    def test_seed_devices_creates_expected_rooms_and_devices(self):
        call_command('seed_devices')

        self.assertEqual(Room.objects.count(), 3)
        self.assertEqual(Device.objects.count(), 15)

    def test_seed_devices_creates_two_fans_and_three_lights_per_room(self):
        call_command('seed_devices')

        for room in Room.objects.all():
            self.assertEqual(
                room.devices.filter(device_type=Device.DeviceType.FAN).count(),
                2,
            )
            self.assertEqual(
                room.devices.filter(device_type=Device.DeviceType.LIGHT).count(),
                3,
            )


class DeviceModelTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name='Test Room', slug='test-room')
        self.device = Device.objects.create(
            room=self.room,
            name='Test Fan',
            device_type=Device.DeviceType.FAN,
            wattage=60,
        )

    def test_set_status_on_sets_current_power_to_wattage(self):
        self.device.set_status(Device.Status.ON)

        self.assertEqual(self.device.status, Device.Status.ON)
        self.assertEqual(self.device.current_power, self.device.wattage)

    def test_set_status_off_sets_current_power_to_zero(self):
        self.device.set_status(Device.Status.ON)
        self.device.set_status(Device.Status.OFF)

        self.assertEqual(self.device.status, Device.Status.OFF)
        self.assertEqual(self.device.current_power, 0)


class SnapshotApiTests(TestCase):
    def test_snapshot_returns_expected_top_level_keys(self):
        call_command('seed_devices')

        response = self.client.get(reverse('snapshot'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'summary')
        self.assertContains(response, 'usage')
        self.assertContains(response, 'rooms')
        self.assertContains(response, 'alerts')

        data = response.json()
        self.assertIn('summary', data)
        self.assertIn('usage', data)
        self.assertIn('rooms', data)
        self.assertIn('alerts', data)
        self.assertIn('estimated_hourly_kwh', data['usage'])
        self.assertIn('estimated_daily_kwh', data['usage'])
        self.assertIn('estimated_daily_cost', data['usage'])

    def test_toggle_device_endpoint_updates_device_status(self):
        room = Room.objects.create(name='Test Room', slug='test-room')
        device = Device.objects.create(
            room=room,
            name='Test Light',
            device_type=Device.DeviceType.LIGHT,
            wattage=15,
        )

        response = self.client.post(
            reverse('toggle-device', kwargs={'device_id': device.id})
        )
        device.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(device.status, Device.Status.ON)
        self.assertEqual(device.current_power, device.wattage)

    def test_status_summary_returns_bot_friendly_fields(self):
        call_command('seed_devices')
        device = Device.objects.get(room__slug='work1', name='Fan 1')
        device.set_status(Device.Status.ON)
        device.save(update_fields=[
            'status',
            'current_power',
            'last_changed',
            'turned_on_at',
        ])

        response = self.client.get(reverse('status-summary'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('rooms', data)
        self.assertIn('total_power', data)
        self.assertIn('devices_on', data)
        self.assertIn('active_alerts', data)

        work_room = next(room for room in data['rooms'] if room['name'] == 'Work Room 1')
        self.assertEqual(work_room['fans_on'], 1)
        self.assertEqual(work_room['lights_on'], 0)
        self.assertEqual(work_room['total_fans'], 2)
        self.assertEqual(work_room['total_lights'], 3)
        self.assertEqual(work_room['power'], 60)

    def test_room_detail_includes_bot_friendly_summary(self):
        call_command('seed_devices')

        response = self.client.get(reverse('room-detail', kwargs={'slug': 'work1'}))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('summary', data)
        self.assertIn('fans_on', data['summary'])
        self.assertIn('lights_on', data['summary'])
