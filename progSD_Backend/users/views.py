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


