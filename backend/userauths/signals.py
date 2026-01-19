from django.db.models.signals import post_delete
from django.dispatch import receiver

from backend.storage_utils import delete_field_file, delete_s3_prefix, user_prefix
from userauths.models import Profile, User


@receiver(post_delete, sender=User)
def delete_user_files_prefix(sender, instance: User, **kwargs):
    if getattr(instance, "id", None):
        delete_s3_prefix(user_prefix(instance.id))


@receiver(post_delete, sender=Profile)
def delete_profile_image_file(sender, instance: Profile, **kwargs):
    delete_field_file(instance, "image", skip_names={"default/default-user.jpg"})
