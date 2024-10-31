from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('operator', 'Operator'),
        ('manager', 'Manager'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.usernam

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add fields specific to customers
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_renting = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Customer Profile"



class OperatorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add fields specific to operators
    work_shift = models.CharField(max_length=50, blank=True)
    assigned_area = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Operator Profile"



class ManagerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add fields specific to managers
    department = models.CharField(max_length=100, blank=True)
    reports_to = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Manager Profile"