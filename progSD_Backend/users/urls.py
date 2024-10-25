from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('api/', views.test_api, name="test_api"),
    # path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('add_location/', views.add_location, name="add_location"),
    path('list_locations/', views.list_locations, name="list_locations"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('list_vehicles/', views.list_vehicles, name="list_vehicles"),
    # path('logout/', views.logout_view, name="logout"),
    path('fetch-data/vehicles', views.fetch_data_vehicles, name='fetch_data_vehicles'),
    path('list-tables/', views.list_tables, name='list_tables'),
]
