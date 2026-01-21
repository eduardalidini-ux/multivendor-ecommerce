from django.conf import settings
from django.db import models


class CourierProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courier_profile",
    )
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Courier Profiles"

    def __str__(self):
        return f"CourierProfile({self.user_id})"


class WarehouseManagerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="warehouse_manager_profile",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Warehouse Manager Profiles"

    def __str__(self):
        return f"WarehouseManagerProfile({self.user_id})"


SHIPMENT_STATUS = (
    ("pending_assignment", "Pending Assignment"),
    ("assigned", "Assigned"),
    ("picked_up", "Picked Up"),
    ("out_for_delivery", "Out For Delivery"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
    ("returned", "Returned"),
)


class Shipment(models.Model):
    order = models.OneToOneField(
        "store.CartOrder",
        on_delete=models.CASCADE,
        related_name="shipment",
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courier_shipments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_shipments",
    )
    status = models.CharField(max_length=50, choices=SHIPMENT_STATUS, default="pending_assignment")
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Shipments"

    def __str__(self):
        return f"Shipment(order={self.order_id})"


SHIPMENT_EVENT_TYPE = (
    ("created", "Created"),
    ("assigned", "Assigned"),
    ("picked_up", "Picked Up"),
    ("out_for_delivery", "Out For Delivery"),
    ("delivered", "Delivered"),
    ("failed", "Failed"),
    ("returned", "Returned"),
    ("note", "Note"),
)


class ShipmentEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50, choices=SHIPMENT_EVENT_TYPE)
    message = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipment_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "Shipment Events"

    def __str__(self):
        return f"ShipmentEvent(shipment={self.shipment_id}, type={self.event_type})"
