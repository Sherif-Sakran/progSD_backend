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
        user =User.objects.create_superuser(
            username=username,
            email=email,
            password=make_password(password)  # This ensures the password is hashed
        )
        # user.is_staff = True
        # Return a success response
        user.save()
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

@csrf_exempt
def logout_view(request):
    if request.method == "POST": 
        logout(request) 
        return JsonResponse({'message': 'You are now logged out'}, status=200)


def fetch_data_vehicles(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Vehicles"')
        rows = cursor.fetchall()
        print('api called')
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



# location insertion example
"""
{
    "name": "Glasgow University",
    "address": "G12 5QQ",
    "latitude": 123.0,
    "longitude": 123.0,
    "vehicle_capacity": 50,
    "number_of_available_vehicles": 50   
}
"""
@csrf_exempt
def add_location(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            location_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        

    location = models.Location(
        name=location_json["name"],
        address=location_json["address"],
        latitude=location_json["latitude"],
        longitude=location_json["longitude"],
        vehicle_capacity=location_json["vehicle_capacity"],
        number_of_available_vehicles=location_json["number_of_available_vehicles"]
    )
    location.save()
    return JsonResponse({'message': 'Location added successfully'}, status=200)


# vehicle insertion example
"""
{
    "type": "Electric Car",
    "battery_level": 100,
    "status": "Available",
    "location_id": 1,
    "last_maintenance_date": "2023-11-18",
    "is_defective": 0
}
"""
@csrf_exempt
def add_vehicle(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            vehicle_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        try:
            # Get the related location instance
            location = models.Location.objects.get(id=vehicle_json["location_id"])
            
            # Create and save the vehicle object
            vehicle = models.Vehicle(
                type=vehicle_json["type"],
                battery_level=vehicle_json["battery_level"],
                status=vehicle_json["status"],
                location=location,
                last_maintenance_date=parse_date(vehicle_json["last_maintenance_date"]),
                is_defective=vehicle_json["is_defective"]
            )
            vehicle.save()
            print("Vehicle created and saved to database.")
            return JsonResponse({'message': 'Vehicle added successfully'}, status=200)
        except models.Location.DoesNotExist:
            return JsonResponse({'message': 'Station location with the given ID does not exist.'}, status=400)

def list_locations(request):
    print('list locations function call')
    current_locations = models.Location.objects.all()
    current_locations_json = []
    for location in current_locations:
        current_locations_json.append(
            {
            "id": location.id,
            "name": location.name,
            "address": location.address,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "vehicle_capacity": location.vehicle_capacity,
            "number_of_available_vehicles": location.number_of_available_vehicles,
            }
        )
    return JsonResponse({'Locations': current_locations_json})

def list_vehicles(request):
    print('list vehicles function call')
    current_vehicles = models.Vehicle.objects.all()
    current_vehicles_json = []
    for vehicle in current_vehicles:
        current_vehicles_json.append(
            {
                "id": vehicle.id,
                "type": vehicle.type,
                "battery_level": vehicle.battery_level,
                "status": vehicle.status,
                "location_id": vehicle.location.id if vehicle.location else None,
                "last_maintenance_date": vehicle.last_maintenance_date.isoformat(),
                "is_defective": vehicle.is_defective,
            }
        )
    return JsonResponse({'All vehicles': current_vehicles_json})


@csrf_exempt
def list_available_vehicles_at(request):
    if request.method == 'POST':
        try:
            location_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        print('list available vehicles at a certain location')
        current_vehicles = models.Vehicle.objects.filter(status='Available', location_id=location_json["location_id"])
        current_vehicles_json = []
        for vehicle in current_vehicles:
            current_vehicles_json.append(
                {
                    "id": vehicle.id,
                    "type": vehicle.type,
                    "battery_level": vehicle.battery_level,
                    "status": vehicle.status,
                    "location_id": vehicle.location.id if vehicle.location else None,
                    "last_maintenance_date": vehicle.last_maintenance_date.isoformat(),
                    "is_defective": vehicle.is_defective,
                }
            )
        return JsonResponse({'Vehicles': current_vehicles_json})


    # choose location (list provided)
    # choose a car (list of available car provided)
@csrf_exempt
def rent_vehicle(request):
    # takes of the car and make its status as rented
    if request.method == 'POST':
        try:
            vehicle_id_JSON = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        print('received car id', vehicle_id_JSON["id"])
        selected_vehicle = models.Vehicle.objects.filter(id=vehicle_id_JSON["id"])[0]
        
        
        selected_vehicle_json = {
            "id": selected_vehicle.id,
            "type": selected_vehicle.type,
            "battery_level": selected_vehicle.battery_level,
            "status": selected_vehicle.status,
            "location_id": selected_vehicle.location.id if selected_vehicle.location else None,
            "last_maintenance_date": selected_vehicle.last_maintenance_date.isoformat(),
            "is_defective": selected_vehicle.is_defective,
        }
        selected_vehicle.status = 'Rented'
        selected_vehicle.save()
        # a row to be added to the rentals table
        return JsonResponse({'Vehicle rented successfully': selected_vehicle_json})