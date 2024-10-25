from django.db import models
# Create your models here.


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20)
    battery_level = models.IntegerField()
    status = models.CharField(max_length=20)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='vehicles')
    last_maintenance_date = models.DateField()
    is_defective = models.BooleanField(default=False)

    def __str__(self):
        return f"Vehicle ID: {self.id} - type: {self.type} - Status: {self.status} - Battery: {self.battery_level}%"



class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    vehicle_capacity = models.IntegerField()
    number_of_available_vehicles = models.IntegerField(default=0)

    
    def __str__(self):
        return f"Location: {self.name} - Capacity: {self.vehicle_capacity} - Available: {self.number_of_available_vehicles}"
