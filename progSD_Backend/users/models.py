from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('operator', 'Operator'),
        ('manager', 'Manager'),
    )
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    class Meta:
            permissions = [
                ("rent_vehicle", "Can rent vehicle"),
                ("return_vehicle", "Can return vehicle"),
                ("report_defective_vehicle", "Can report defective vehicle"),
                ("pay_charges", "Can pay charges"),
                ("track_vehicle", "Can track vehicle"),
                ("charge_vehicle", "Can charge vehicle"),
                ("repair_vehicle", "Can repair vehicle"),
                ("move_vehicle", "Can move vehicle"),
                ("generate_reports", "Can generate reports"),
                ("request_discount", "Can request discounts"),
                ("verify_requests", "Can verify request"),
            ]
    
    
    def __str__(self):
        return self.username

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add fields specific to customers
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_renting = models.BooleanField(default=False)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
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