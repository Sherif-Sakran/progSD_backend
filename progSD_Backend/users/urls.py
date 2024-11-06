from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout_view"),
    path('is_renting/', views.is_renting, name="is_renting"),
    path('api/', views.test_api, name="test_api"),
    path('get_rental_list/', views.get_rental_list, name="get_rental_list"),
    path('get_defect_report_list/', views.get_defect_report_list, name="get_defect_report_list"),
    path('get_discount_request_list/', views.get_discount_request_list, name="get_discount_request_list"),
    path('get_coupon_use_list/', views.get_coupon_use_list, name="get_coupon_use_list"),
    path('get_payment_list/', views.get_payment_list, name="get_payment_list"),
]
