from django.urls import path

from warehouse import views


urlpatterns = [
    path("couriers/", views.CourierListAPIView.as_view()),
    path("orders/unassigned/", views.UnassignedOrdersAPIView.as_view()),
    path("assign/", views.AssignCourierAPIView.as_view()),
    path("courier/my-shipments/", views.CourierMyShipmentsAPIView.as_view()),
    path("courier/shipment/<int:shipment_id>/status/", views.CourierShipmentStatusUpdateAPIView.as_view()),
    path("track/order/<str:order_oid>/", views.TrackOrderAPIView.as_view()),
]
