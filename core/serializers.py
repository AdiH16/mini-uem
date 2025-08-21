from rest_framework import serializers
from .models import Owner, Device, Policy, DevicePolicy

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ["id", "name", "email"]

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ["id", "name", "type", "payload", "created_at"]
        read_only_fields = ["created_at"]

class DevicePolicySerializer(serializers.ModelSerializer):
    policy = PolicySerializer(read_only=True)

    class Meta:
        model = DevicePolicy
        fields = ["policy", "status", "assigned_at", "last_applied_at"]

class DeviceSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=Owner.objects.all(), source="owner", write_only=True, required=False, allow_null=True
    )

    assignments = DevicePolicySerializer(source="devicepolicy_set", many=True, read_only=True)

    class Meta:
        model = Device
        fields = [
            "id", "device_name", "os_type", "status", "last_check_in",
            "owner", "owner_id", "assignments", "created_at", "updated_at"
        ]
        read_only_fields = ["last_check_in", "created_at", "updated_at"]