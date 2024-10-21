from django.urls import path
from . import views
from .views import fetch_data_vehicles, list_tables

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    # path('logout/', views.logout_view, name="logout"),
    path('fetch-data/vehicles', fetch_data_vehicles, name='fetch_data_vehicles'),
    path('list-tables/', list_tables, name='list_tables'),
]
