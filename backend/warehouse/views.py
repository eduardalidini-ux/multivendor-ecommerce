from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import CartOrder, CartOrderItem
from store.serializers import CartOrderSerializer
from userauths.models import User
from warehouse.models import CourierProfile, Shipment, ShipmentEvent
from warehouse.permissions import IsCourier, IsWarehouseManager
from warehouse.serializers import ShipmentSerializer, UserLiteSerializer


class CourierListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = UserLiteSerializer

    def get_queryset(self):
        courier_user_ids = CourierProfile.objects.filter(is_active=True).values_list("user_id", flat=True)
        return User.objects.filter(id__in=courier_user_ids)


class UnassignedOrdersAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = CartOrderSerializer

    def get_queryset(self):
        return (
            CartOrder.objects.filter(payment_status="paid")
            .filter(Q(shipment__isnull=True) | Q(shipment__courier__isnull=True))
            .order_by("-date")
        )


class WarehouseShipmentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        qs = Shipment.objects.select_related("order", "courier", "assigned_by")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class AssignCourierAPIView(APIView):
    permission_classes = [IsAuthenticated, IsWarehouseManager]

    @transaction.atomic
    def post(self, request):
        order_oid = request.data.get("order_oid")
        order_id = request.data.get("order_id")
        courier_user_id = request.data.get("courier_user_id")

        if not courier_user_id:
            return Response({"message": "courier_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if order_oid:
            order = get_object_or_404(CartOrder.objects.select_for_update(), oid=order_oid)
        elif order_id:
            order = get_object_or_404(CartOrder.objects.select_for_update(), id=order_id)
        else:
            return Response({"message": "order_oid or order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        courier_profile = CourierProfile.objects.filter(user_id=courier_user_id, is_active=True).first()
        if not courier_profile:
            return Response({"message": "Invalid courier"}, status=status.HTTP_400_BAD_REQUEST)

        shipment, created = Shipment.objects.select_for_update().get_or_create(order=order)
        shipment.courier_id = courier_user_id
        shipment.assigned_by = request.user
        shipment.assigned_at = timezone.now()
        shipment.status = "assigned"
        shipment.save()

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type="assigned",
            message=f"Assigned to courier user_id={courier_user_id}",
            created_by=request.user,
        )

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)


class CourierMyShipmentsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCourier]
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        return Shipment.objects.filter(courier=self.request.user).select_related("order", "courier", "assigned_by")


class CourierShipmentStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCourier]

    @transaction.atomic
    def patch(self, request, shipment_id: int):
        shipment = get_object_or_404(Shipment.objects.select_for_update(), id=shipment_id)
        if shipment.courier_id != request.user.id:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        message = request.data.get("message")
        if not new_status:
            return Response({"message": "status is required"}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = {c[0] for c in Shipment._meta.get_field("status").choices}
        if new_status not in valid_statuses:
            return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        shipment.status = new_status
        now = timezone.now()
        if new_status == "picked_up":
            shipment.picked_up_at = shipment.picked_up_at or now
        if new_status == "delivered":
            shipment.delivered_at = shipment.delivered_at or now

        shipment.save()

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=new_status if new_status in {c[0] for c in ShipmentEvent._meta.get_field("event_type").choices} else "note",
            message=message,
            created_by=request.user,
        )

        if new_status == "delivered":
            CartOrderItem.objects.filter(order=shipment.order).update(delivery_status="Delivered")
            shipment.order.order_status = "Fulfilled"
            shipment.order.save(update_fields=["order_status"])

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)


class TrackOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_oid: str):
        order = get_object_or_404(CartOrder.objects.select_related("buyer"), oid=order_oid)
        shipment = Shipment.objects.filter(order=order).select_related("courier", "assigned_by").first()

        user = request.user
        if not user.is_staff:
            allowed = False
            if order.buyer_id and order.buyer_id == user.id:
                allowed = True
            if not allowed and shipment and shipment.courier_id == user.id:
                allowed = True
            if not allowed:
                wm = getattr(user, "warehouse_manager_profile", None)
                if wm and getattr(wm, "is_active", False):
                    allowed = True
            if not allowed:
                vendor = getattr(user, "vendor", None)
                if vendor and order.vendor.filter(id=vendor.id).exists():
                    allowed = True
            if not allowed:
                return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        payload = {
            "order": CartOrderSerializer(order).data,
            "shipment": ShipmentSerializer(shipment).data if shipment else None,
        }
        return Response(payload, status=status.HTTP_200_OK)
