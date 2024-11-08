from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('Electric Car', 'Electric Car'),
        ('Electric Scooter', 'Electric Scooter'),
        ('Electric Bike', 'Electric Bike'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Defective', 'Defective'),
    ]

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    make = models.CharField(max_length=20, null=True)
    model = models.CharField(max_length=20, null=True)
    battery_level = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    station_id = models.ForeignKey('StationLocation', on_delete=models.SET_NULL, null=True)
    last_maintenance_date = models.DateField()
    is_defective = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.type} - {self.status}'


class VehicleLocation(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        unique_together = ('vehicle_id', 'timestamp')

    def __str__(self):
        return f"Location for {self.vehicle} at {self.timestamp}"


class StationLocation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    vehicle_capacity = models.IntegerField()
    number_of_available_vehicles = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Rental(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    start_location = models.ForeignKey(StationLocation, related_name='rentals_start', on_delete=models.CASCADE)
    end_location = models.ForeignKey(StationLocation, related_name='rentals_end', on_delete=models.CASCADE, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Rental {self.id} by {self.customer}"



# class MaintenanceLog(models.Model):
#     ACTION_TAKEN_CHOICES = [
#         ('Charged', 'Charged'),
#         ('Repaired', 'Repaired'),
#         ('Relocated', 'Relocated'),
#         ('ReportReceived', 'ReportReceived'),
#     ]

#     id = models.AutoField(primary_key=True)
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
#     reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operator_maintenance_logs', null=True)
#     maintenance_date = models.DateField()
#     description = models.TextField()
#     action_taken = models.CharField(max_length=20, choices=ACTION_TAKEN_CHOICES)

#     def __str__(self):
#         return f'Maintenance Log for {self.vehicle}'


class CustomerReportedDefects(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    
    found_defective = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    defect_fixed = models.BooleanField(default=False)

class RepairsLog(models.Model):
    id = models.AutoField(primary_key=True)
    defect = models.ForeignKey(CustomerReportedDefects, on_delete=models.CASCADE)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    repair_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class ChargesLog(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    charge_date = models.DateTimeField(default=timezone.now)
    charge_up_to = models.IntegerField()
    original_battery_level = models.IntegerField()
    notes = models.TextField(blank=True, null=True)



class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('Usage Report', 'Usage Report'),
        ('Revenue Report', 'Revenue Report'),
    ]

    id = models.AutoField(primary_key=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_on = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f'Report {self.report_type} by {self.manager}'


# for the extra functionality of student_discounts
class DiscountRequests(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    student_id_number = models.CharField(max_length=20)
    institution = models.CharField(max_length=100)
    student_email = models.EmailField()
    id_valid_until = models.DateTimeField(blank=True)

    request_date = models.DateTimeField(default=timezone.now)

    response_by_operator = models.TextField(null=True)
    
    is_verified = models.BooleanField(default=False)
    confirmed_date = models.DateTimeField(null=True, blank=True)


class Partner(models.Model):
    CATEGORY_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    joined_date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.category}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    issued_by = models.ForeignKey(Partner, on_delete=models.CASCADE)
    valid_until = models.DateField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_use = models.IntegerField(default=1)

    def is_valid(self):
        return self.valid_until >= timezone.now().date() and self.used_by is None

    def __str__(self):
        return f"Coupon {self.code} - Discount {self.discount}%"


class CouponUse(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Replace with CustomUser if you're using a custom user model
    used_at = models.DateTimeField(auto_now_add=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Coupon {self.code} - Discount {self.discount}%"



class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
    ]

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f'Payment of {self.amount} by {self.customer}'

