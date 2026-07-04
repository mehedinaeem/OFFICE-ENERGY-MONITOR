import random
import time

from django.core.management.base import BaseCommand

from monitor.models import Device


class Command(BaseCommand):
    help = 'Continuously toggle random devices for local simulation.'

    def handle(self, *args, **options):
        if not Device.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    'No devices found. Run python manage.py seed_devices first.'
                )
            )
            return

        self.stdout.write('Starting device simulation. Press Ctrl+C to stop.')

        try:
            while True:
                devices = list(Device.objects.select_related('room').order_by('id'))
                count = min(random.randint(1, 2), len(devices))

                for device in random.sample(devices, count):
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

                    self.stdout.write(
                        f'{device.room.name} - {device.name} changed to '
                        f'{device.status}'
                    )

                time.sleep(5)
        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Device simulation stopped.'))
