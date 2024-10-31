from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, OperatorProfile, ManagerProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'customer':
            CustomerProfile.objects.create(user=instance)
        elif instance.user_type == 'operator':
            OperatorProfile.objects.create(user=instance)
        elif instance.user_type == 'manager':
            ManagerProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'customer':
        instance.customerprofile.save()
    elif instance.user_type == 'operator':
        instance.operatorprofile.save()
    elif instance.user_type == 'manager':
        instance.managerprofile.save()
