from django.db import models
from django.utils import timezone


class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Device(models.Model):
    class DeviceType(models.TextChoices):
        FAN = 'fan', 'Fan'
        LIGHT = 'light', 'Light'

    class Status(models.TextChoices):
        ON = 'ON', 'ON'
        OFF = 'OFF', 'OFF'

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.OFF)
    wattage = models.PositiveIntegerField()
    current_power = models.PositiveIntegerField(default=0)
    last_changed = models.DateTimeField(default=timezone.now)
    turned_on_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.room.name})'

    def set_status(self, new_status):
        if new_status not in self.Status.values:
            raise ValueError(f'Invalid status: {new_status}')

        if self.status == new_status:
            return

        now = timezone.now()
        self.status = new_status
        self.last_changed = now

        if new_status == self.Status.ON:
            self.current_power = self.wattage
            self.turned_on_at = now
        else:
            self.current_power = 0
            self.turned_on_at = None


class Alert(models.Model):
    class Severity(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        DANGER = 'danger', 'Danger'

    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        related_name='alerts',
        null=True,
        blank=True,
    )
    message = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.message
