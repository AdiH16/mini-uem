from django.contrib import admin
from .models import Owner, Device, Policy, DevicePolicy

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'os_type', 'status', 'owner', 'last_check_in')
    search_fields = ('device_name',)
    list_filter = ('os_type', 'status')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    search_fields = ('name',)
    list_filter = ('type',)

@admin.register(DevicePolicy)
class DevicePolicyAdmin(admin.ModelAdmin):
    list_display = ('device', 'policy', 'status', 'assigned_at', 'last_applied_at')
    search_fields = ('device__device_name', 'policy__name')
    list_filter = ('status',)