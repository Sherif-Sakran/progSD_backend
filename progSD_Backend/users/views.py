import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt


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
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        
        # Get data from the parsed JSON
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        # Validate input (you can add more validations if necessary)
        if not username or not password:
            return JsonResponse({'message': 'Username and password are required'}, status=400)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already taken'}, status=400)

        # Create the user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  # This ensures the password is hashed
        )

        # Return a success response
        return JsonResponse({'message': 'User registered successfully'}, status=201)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    # return HttpResponse('Registration is here')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        
        # Get data from the parsed JSON
        username = data.get('username')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            # Invalid credentials
            return JsonResponse({'message': 'Invalid username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    # return HttpResponse('Login is here')
    
def fetch_data_vehicles(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Vehicles"')
        rows = cursor.fetchall()
    return JsonResponse({'data': rows})

def list_tables(request):
    # Query to get all table names from the 'public' schema
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        tables = cursor.fetchall()
    
    # Return the list of tables as a JSON response
    return JsonResponse({'tables': [table[0] for table in tables]})