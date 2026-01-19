from django.db.models.signals import post_delete
from django.dispatch import receiver

from backend.storage_utils import delete_field_file
from store.models import Brand, Category, Color, Gallery, Product


@receiver(post_delete, sender=Category)
def delete_category_image_file(sender, instance: Category, **kwargs):
    delete_field_file(instance, "image", skip_names={"category.jpg"})


@receiver(post_delete, sender=Brand)
def delete_brand_image_file(sender, instance: Brand, **kwargs):
    delete_field_file(instance, "image", skip_names={"brand.jpg"})


@receiver(post_delete, sender=Product)
def delete_product_image_file(sender, instance: Product, **kwargs):
    delete_field_file(instance, "image", skip_names={"product.jpg"})


@receiver(post_delete, sender=Gallery)
def delete_gallery_image_file(sender, instance: Gallery, **kwargs):
    delete_field_file(instance, "image", skip_names={"gallery.jpg"})


@receiver(post_delete, sender=Color)
def delete_color_image_file(sender, instance: Color, **kwargs):
    delete_field_file(instance, "image")
