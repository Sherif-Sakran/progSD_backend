from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    # path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('add_location/', views.add_location, name="add_location"),
    path('list_locations/', views.list_locations, name="list_locations"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('rent_vehicle/', views.rent_vehicle, name="rent_vehicle"),
    path('return_vehicle/', views.return_vehicle, name="return_vehicle"),
    path('list_vehicles/', views.list_vehicles, name="list_vehicles"),
    path('list_available_vehicles_at/', views.list_available_vehicles_at, name="list_available_vehicles_at"),
    # path('logout/', views.logout_view, name="logout"),
    path('fetch-data/vehicles', views.fetch_data_vehicles, name='fetch_data_vehicles'),
    path('list-tables/', views.list_tables, name='list_tables'),
]
