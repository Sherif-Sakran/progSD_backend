from django.contrib import admin
from .models import CustomUser
from vehicles.models import Vehicle, VehicleLocation, StationLocation, Rental, Payment, MaintenanceLog, Report

admin.site.register(CustomUser)
admin.site.register(Vehicle)
admin.site.register(VehicleLocation)
admin.site.register(StationLocation)
admin.site.register(Rental)
admin.site.register(Payment)
admin.site.register(MaintenanceLog)
admin.site.register(Report)
