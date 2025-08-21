from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, OwnerViewSet, DeviceViewSet, PolicyViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r"owners", OwnerViewSet, basename="owner")
router.register(r"devices", DeviceViewSet, basename="device")
router.register(r"policies", PolicyViewSet, basename="policy")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]