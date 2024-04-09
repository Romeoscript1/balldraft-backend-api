from profiles.models import Profile
from django.db.models.signals import pre_save
from  django.dispatch import receiver
import uuid

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