from django.db.models.signals import post_delete
from django.dispatch import receiver

from backend.storage_utils import delete_field_file, delete_s3_prefix, user_prefix
from vendor.models import Vendor


@receiver(post_delete, sender=Vendor)
def delete_vendor_image_file(sender, instance: Vendor, **kwargs):
    if getattr(instance, "user_id", None):
        prefix = user_prefix(instance.user_id)
        delete_s3_prefix(prefix)
        delete_field_file(
            instance,
            "image",
            skip_names={"shop-image.jpg"},
            required_prefixes={prefix},
        )
    else:
        delete_field_file(instance, "image", skip_names={"shop-image.jpg"})
