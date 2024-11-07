import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
import json
from . import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required
from vehicles import models



User = get_user_model()  # this will now refer to CustomUser



@csrf_exempt
def test_api(request):
    if request.method == 'POST':
        # Get data from the request
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        # Return the received data in a JSON response
        return JsonResponse({'message': 'Data received', 'data': data}, status=200)
    else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        role = data.get('role')  # Role field in request data

        User = get_user_model()  # Use the custom user model
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already taken'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password, role=role)

        # Assign permissions based on role
        if role == 'customer':
            permissions = ['rent_vehicle', 'return_vehicle', 'report_defective_vehicle', 'pay_charges', 'request_discount']
        elif role == 'operator':
            permissions = ['track_vehicle', 'charge_vehicle', 'repair_vehicle', 'move_vehicle', 'verify_requests']
        elif role == 'manager':
            permissions = ['generate_reports', 'add_partners']
        else:
            permissions = []

        for perm_codename in permissions:
            perm = Permission.objects.get(codename=perm_codename)
            user.user_permissions.add(perm)

        user.save()
        return JsonResponse({'message': 'User registered successfully',
                             'permissions granted': permissions}, status=201)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    # return HttpResponse('Signup is here')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)


            role = user.role
            permissions = user.get_all_permissions()
            json_return = {
                'message': 'Login successful',
                'username': user.username,
                'role': role,
                'permissions': list(permissions),
            }
            
            if hasattr(user, 'customerprofile'):
                json_return['is_renting'] = user.customerprofile.is_renting


            return JsonResponse(json_return, status=200)
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        # return HttpResponse('Login is here')


@login_required
def is_renting(request):
    if request.method == "GET":
        is_user_renting = hasattr(request.user, 'customerprofile') and request.user.customerprofile.is_renting
        return JsonResponse({'is_renting': is_user_renting}, status=200)


@csrf_exempt
def logout_view(request):
    if request.method == "POST": 
        logout(request) 
        return JsonResponse({'message': 'You are now logged out'}, status=200)


@login_required
def get_rental_list(request):
    rentals = models.Rental.objects.filter(customer=request.user)
    rentals_list = [
        {
            'id': rental.id,
            'vehicle_id': rental.vehicle.id,
            'vehicle_type': rental.vehicle.type,
            'vehicle_make': rental.vehicle.make,
            'vehicle_model  ': rental.vehicle.model,
            'start_time': rental.start_time,
            'end_time': rental.end_time,
            'start_location': rental.start_location.name,
            'end_location': rental.end_location.name if rental.end_location else None,
            'total_cost': rental.total_cost,
            'is_active': rental.is_active,
        }
        for rental in rentals
    ]
    return JsonResponse(rentals_list, safe=False)

@login_required
def get_defect_report_list(request):
    defects = models.CustomerReportedDefects.objects.filter(reported_by=request.user)
    defects_list = [
        {
            'id': defect.id,
            'vehicle': defect.vehicle.model,
            'report_date': defect.report_date,
            'description': defect.description,
            'found_defective': defect.found_defective,
            'confirmed_date': defect.confirmed_date,
        }
        for defect in defects
    ]
    return JsonResponse(defects_list, safe=False)

@login_required
def get_discount_request_list(request):
    discount_requests = models.DiscountRequests.objects.filter(customer=request.user)
    discount_requests_list = [
        {
            'id': discount_request.id,
            'student_id_number': discount_request.student_id_number,
            'institution': discount_request.institution,
            'student_email': discount_request.student_email,
            'request_date': discount_request.request_date,
            'response_by_operator': discount_request.response_by_operator,
            'is_verified': discount_request.is_verified,
            'confirmed_date': discount_request.confirmed_date,
        }
        for discount_request in discount_requests
    ]
    return JsonResponse(discount_requests_list, safe=False)

@login_required
def get_coupon_use_list(request):
    coupons = models.CouponUse.objects.filter(user=request.user)
    coupons_list = [
        {
            'coupon_code': coupon.coupon.code,
            'used_at': coupon.used_at,
            'discount_applied': coupon.discount_applied,
        }
        for coupon in coupons
    ]
    return JsonResponse(coupons_list, safe=False)

@login_required
def get_payment_list(request):
    payments = models.Payment.objects.filter(customer=request.user)
    payments_list = [
        {
            'id': payment.id,
            'rental_id': payment.rental.id,
            'amount': payment.amount,
            'timestamp': payment.timestamp,
            'payment_method': payment.payment_method,
        }
        for payment in payments
    ]
    return JsonResponse(payments_list, safe=False)
