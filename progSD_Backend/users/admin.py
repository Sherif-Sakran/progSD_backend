from django.contrib import admin
from .models import CustomUser
from vehicles.models import Vehicle, VehicleLocation, StationLocation, Rental, Payment, CustomerReportedDefects, RepairsLog, Report

admin.site.register(CustomUser)
admin.site.register(Vehicle)
admin.site.register(VehicleLocation)
admin.site.register(StationLocation)
admin.site.register(Rental)
admin.site.register(Payment)
admin.site.register(CustomerReportedDefects)
admin.site.register(RepairsLog)
admin.site.register(Report)
