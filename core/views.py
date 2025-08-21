from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Owner, Device, Policy, DevicePolicy
from .serializers import OwnerSerializer, DeviceSerializer, PolicySerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all().order_by('id')
    serializer_class = OwnerSerializer

class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all().order_by('id')
    serializer_class = PolicySerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related("owner").prefetch_related("policies").order_by("-id")
    serializer_class = DeviceSerializer

    @action(detail=True, methods=["POST"], permission_classes=[AllowAny])
    def check_in(self, request, pk=None):
        # Simulate a device heartbeat: update last_check_in timestamp
        device = self.get_object()
        device.last_check_in = timezone.now()
        device.save(update_fields=["last_check_in"])
        return Response({"ok": True, "last_check_in": device.last_check_in})
    
    @action(detail=True, methods=["POST"])
    def assign_policy(self, request, pk=None):
        """
        Assign a policy to this device.
        Body: { "policy_id": <int> }
        """
        device = self.get_object()
        policy_id = request.data.get("policy_id")
        if not policy_id:
            return Response({"detail": "policy_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            policy = Policy.objects.get(pk=policy_id)
        except Policy.DoesNotExist:
            return Response({"detail": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)
        
        assignment, created = DevicePolicy.objects.get_or_create(device=device, policy=policy)
        if not created:
            # Already exists; keep current status
            msg = "already_assigned"
        else:
            msg = "assigned"

        return Response({"ok": True, "result": msg, "device_id": device.id, "policy_id": policy.id})