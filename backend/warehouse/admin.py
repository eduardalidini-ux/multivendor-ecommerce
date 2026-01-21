from django.contrib import admin

from warehouse.models import CourierProfile, Shipment, ShipmentEvent, WarehouseManagerProfile


@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["user__email", "user__username", "user__full_name"]


@admin.register(WarehouseManagerProfile)
class WarehouseManagerProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["user__email", "user__username", "user__full_name"]


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "courier", "status", "assigned_at", "picked_up_at", "delivered_at", "created_at"]
    list_filter = ["status"]
    search_fields = ["order__oid", "courier__email", "courier__username", "courier__full_name"]
    inlines = [ShipmentEventInline]


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):
    list_display = ["id", "shipment", "event_type", "created_by", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["shipment__order__oid", "created_by__email", "message"]
