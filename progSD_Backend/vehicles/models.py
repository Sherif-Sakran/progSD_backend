from django.db import models
from django.contrib.auth import get_user_model

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
    battery_level = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    station_id = models.ForeignKey('StationLocation', on_delete=models.CASCADE)
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


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
    ]

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f'Payment of {self.amount} by {self.customer}'



class MaintenanceLog(models.Model):
    ACTION_TAKEN_CHOICES = [
        ('Charged', 'Charged'),
        ('Repaired', 'Repaired'),
        ('Relocated', 'Relocated'),
    ]

    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    description = models.TextField()
    action_taken = models.CharField(max_length=20, choices=ACTION_TAKEN_CHOICES)

    def __str__(self):
        return f'Maintenance Log for {self.vehicle}'



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
