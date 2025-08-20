from django.db import models
from django.utils import timezone

class Owner(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
    
class Device(models.Model):
    class OSType(models.TextChoices):
        ANDROID = "android", "Android"
        CHROME = "chrome", "ChromeOS"

    class DeviceStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    owner = models.ForeignKey(Owner, null=True, blank=True, on_delete=models.SET_NULL, related_name="devices")
    device_name = models.CharField(max_length=120, db_index=True)
    os_type = models.CharField(max_length=16, choices=OSType.choices)
    status = models.CharField(max_length=16, choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE)
    last_check_in = models.DateTimeField(null=True, blank=True, db_index=True)

    policies = models.ManyToManyField("Policy", through="DevicePolicy", related_name="devices")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_in(self):
        self.last_check_in = timezone.now()
        self.save(update_fields=["last_check_in"])

    def __str__(self):
        return f"{self.device_name} ({self.os_type})"
    
class Policy(models.Model):
    class PolicyType(models.TextChoices):
        WIFI = "wifi", "WiFi"
        APP = "app", "App Install"
        RESTRICTION = "restriction", "Restriction"

    name = models.CharField(max_length=120, unique=True)
    type = models.CharField(max_length=16, choices=PolicyType.choices)
    payload = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.type}]"
    
class DevicePolicy(models.Model):
    class AssignStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPLIED = "applied", "Applied"
        FAILED = "failed", "Failed"

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_applied_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=AssignStatus.choices, default=AssignStatus.PENDING)

    class Meta:
        unique_together = ("device", "policy")
        indexes = [
            models.Index(fields=["device", "status"]),
        ]

    def __str__(self):
        return f"{self.device} -> {self.policy} ({self.status})"