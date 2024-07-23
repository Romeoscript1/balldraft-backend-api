from profiles.models import Profile
from django.db.models.signals import pre_save, post_save
from  django.dispatch import receiver
import uuid
from django.conf import settings
from .models import Profile

@receiver(pre_save,  sender=Profile)
def set_user_name(sender, instance, **kwargs):
    if not instance.username:
        username = f"{instance.user.first_name}.{instance.user.last_name}".lower()
        unique_id = str(uuid.uuid4())[:8]
        counter = 1
        while  Profile.objects.filter(username=username):
            username =  f"{instance.user.first_name.lower()}.{instance.user.last_name.lower()}.{unique_id}"
            counter += 1
        instance.username = username
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)