from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, OperatorProfile, ManagerProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'customer':
            CustomerProfile.objects.create(user=instance)
        elif instance.role == 'operator':
            OperatorProfile.objects.create(user=instance)
        elif instance.role == 'manager':
            ManagerProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'customer':
        instance.customerprofile.save()
    elif instance.role == 'operator':
        instance.operatorprofile.save()
    elif instance.role == 'manager':
        instance.managerprofile.save()
