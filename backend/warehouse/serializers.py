from rest_framework import serializers

from userauths.models import User
from store.models import CartOrder
from warehouse.models import Shipment, ShipmentEvent


class UserLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "full_name"]


class ShipmentEventSerializer(serializers.ModelSerializer):
    created_by = UserLiteSerializer(read_only=True)

    class Meta:
        model = ShipmentEvent
        fields = "__all__"


class CartOrderLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = [
            "id",
            "oid",
            "full_name",
            "email",
            "mobile",
            "address",
            "city",
            "state",
            "country",
            "payment_status",
            "order_status",
            "total",
            "date",
        ]


class ShipmentSerializer(serializers.ModelSerializer):
    order = CartOrderLiteSerializer(read_only=True)
    courier = UserLiteSerializer(read_only=True)
    assigned_by = UserLiteSerializer(read_only=True)
    events = ShipmentEventSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = "__all__"
