from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout_view"),
    path('is_renting/', views.is_renting, name="is_renting"),
    path('api/', views.test_api, name="test_api"),
]
