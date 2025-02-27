from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    # path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('add_location/', views.add_location, name="add_location"),
    path('list_locations/', views.list_locations, name="list_locations"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('rent_vehicle/', views.rent_vehicle, name="rent_vehicle"),
    path('charge_account/', views.charge_account, name="charge_account"),
    path('pay_charges/', views.pay_charges, name="pay_charges"),
    path('update_vehicle_location/', views.update_vehicle_location, name="update_vehicle_location"),
    path('return_vehicle/', views.return_vehicle, name="return_vehicle"),
    path('report_defective_vehicle/', views.report_defective_vehicle, name="report_defective_vehicle"),
    path('confirm_defective_vehicle/', views.confirm_defective_vehicle, name="confirm_defective_vehicle"),
    path('repair_vehicle/', views.repair_vehicle, name="repair_vehicle"),
    path('charge_vehicle/', views.charge_vehicle, name="charge_vehicle"),
    path('list_low_battery_vehicles/', views.list_low_battery_vehicles, name="list_low_battery_vehicles"),
    path('move_vehicle/', views.move_vehicle, name="move_vehicle"),
    path('track_vehicle/', views.track_vehicle, name="track_vehicle"),
    path('add_partner/', views.add_partner, name="add_partner"),
    path('add_coupon/', views.add_coupon, name="add_coupon"),
    path('request_discount/', views.request_discount, name="request_discount"),
    path('get_unverified_requests/', views.get_unverified_requests, name="get_unverified_requests"),
    path('get_defect_reports/', views.get_defect_reports, name="get_defect_reports"),
    path('verify_discount_request/', views.verify_discount_request, name="verify_discount_request"),
    path('list_vehicles/', views.list_vehicles, name="list_vehicles"),
    path('list_partners/', views.list_partners, name="list_partners"),
    path('list_available_vehicles_at/', views.list_available_vehicles_at, name="list_available_vehicles_at"),
    path('fetch_vehicles/', views.list_locations, name="list_locations"),
    path('fetch-data/vehicles', views.fetch_data_vehicles, name='fetch_data_vehicles'),
    path('list-tables/', views.list_tables, name='list_tables'),
]
