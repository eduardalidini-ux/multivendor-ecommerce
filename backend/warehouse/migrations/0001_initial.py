from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0030_pg_trgm_product_title_idx"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourierProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("phone", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "vehicle_type",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courier_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Courier Profiles",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Shipment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_assignment", "Pending Assignment"),
                            ("assigned", "Assigned"),
                            ("picked_up", "Picked Up"),
                            ("out_for_delivery", "Out For Delivery"),
                            ("delivered", "Delivered"),
                            ("failed", "Failed"),
                            ("returned", "Returned"),
                        ],
                        default="pending_assignment",
                        max_length=50,
                    ),
                ),
                ("assigned_at", models.DateTimeField(blank=True, null=True)),
                ("picked_up_at", models.DateTimeField(blank=True, null=True)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_shipments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "courier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="courier_shipments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipment",
                        to="store.cartorder",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Shipments",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="WarehouseManagerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="warehouse_manager_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Warehouse Manager Profiles",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="ShipmentEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("assigned", "Assigned"),
                            ("picked_up", "Picked Up"),
                            ("out_for_delivery", "Out For Delivery"),
                            ("delivered", "Delivered"),
                            ("failed", "Failed"),
                            ("returned", "Returned"),
                            ("note", "Note"),
                        ],
                        max_length=50,
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="shipment_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "shipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="warehouse.shipment",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Shipment Events",
                "ordering": ["created_at"],
            },
        ),
    ]
