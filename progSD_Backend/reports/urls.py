from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('total_payments_per_location/', views.total_payments_per_location, name="total_payments_per_location"),
    path('most_used_vehicle_types/', views.most_used_vehicle_types, name="most_used_vehicle_types"),
    path('vehicles_currently_in_use/', views.vehicles_currently_in_use, name="vehicles_currently_in_use"),
    path('most_popular_rental_locations/', views.most_popular_rental_locations, name="most_popular_rental_locations"),
    path('most_popular_destination_locations/', views.most_popular_destination_locations, name="most_popular_destination_locations"),
]
