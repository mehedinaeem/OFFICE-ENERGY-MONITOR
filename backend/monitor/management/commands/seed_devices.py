from django.core.management.base import BaseCommand

from monitor.models import Device, Room


class Command(BaseCommand):
    help = 'Seed initial office rooms and devices.'

    def handle(self, *args, **options):
        rooms = [
            ('Drawing Room', 'drawing'),
            ('Work Room 1', 'work1'),
            ('Work Room 2', 'work2'),
        ]

        device_templates = [
            ('Fan 1', Device.DeviceType.FAN, 60),
            ('Fan 2', Device.DeviceType.FAN, 60),
            ('Light 1', Device.DeviceType.LIGHT, 15),
            ('Light 2', Device.DeviceType.LIGHT, 15),
            ('Light 3', Device.DeviceType.LIGHT, 15),
        ]

        for room_name, room_slug in rooms:
            room, _ = Room.objects.get_or_create(
                slug=room_slug,
                defaults={
                    'name': room_name,
                    'description': '',
                },
            )

            if room.name != room_name:
                room.name = room_name
                room.save(update_fields=['name'])

            for device_name, device_type, wattage in device_templates:
                Device.objects.update_or_create(
                    room=room,
                    name=device_name,
                    defaults={
                        'device_type': device_type,
                        'wattage': wattage,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS('Rooms and 15 devices seeded successfully.')
        )
