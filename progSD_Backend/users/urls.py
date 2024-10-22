from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('api/', views.test_api, name="test_api"),
    # path('logout/', views.logout_view, name="logout"),
    path('fetch-data/vehicles', views.fetch_data_vehicles, name='fetch_data_vehicles'),
    path('list-tables/', views.list_tables, name='list_tables'),
]
