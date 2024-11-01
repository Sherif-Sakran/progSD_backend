import json
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
import json
from . import models
from django.utils import timezone
from geopy.distance import geodesic
from decimal import Decimal



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
        

    location = models.StationLocation(
        name=location_json["name"],
        address=location_json["address"],
        latitude=location_json["latitude"],
        longitude=location_json["longitude"],
        vehicle_capacity=location_json["vehicle_capacity"],
        number_of_available_vehicles=location_json["number_of_available_vehicles"]
    )
    location.save()
    return JsonResponse({'message': 'Location added successfully', 'Station': location_json}, status=200)


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
            station_location = models.StationLocation.objects.get(id=vehicle_json["location_id"])
            
            # Create and save the vehicle object
            vehicle = models.Vehicle(
                type=vehicle_json["type"],
                battery_level=vehicle_json["battery_level"],
                status=vehicle_json["status"],
                station_id=station_location,
                last_maintenance_date=parse_date(vehicle_json["last_maintenance_date"]),
                is_defective=vehicle_json["is_defective"]
            )
            vehicle.save()
            print("Vehicle created and saved to database.")
            return JsonResponse({'message': 'Vehicle added successfully', 'vehicle': vehicle_json}, status=200)
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
    if not request.user.has_perm('users.rent_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)


    if request.method == 'POST':
        if request.user.customerprofile.is_renting:
            return JsonResponse({'message': 'You cannot rent more than once at the same time'}, status=400)

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
            "station_location": selected_vehicle.station_id.id if selected_vehicle.station_id else None,
            "last_maintenance_date": selected_vehicle.last_maintenance_date.isoformat(),
            "is_defective": selected_vehicle.is_defective,
        }
        selected_vehicle.status = 'Rented'
        
        rental_record = models.Rental.objects.create(
            customer=request.user,
            vehicle=selected_vehicle,
            start_time=timezone.now(),
            start_location=selected_vehicle.station_id,
            is_active=True
        )

        rental_record_json = {
            "id": rental_record.id,
            "customer": rental_record.customer.id,
            "vehicle": selected_vehicle_json,
            "start_time": rental_record.start_time.isoformat(),
            "start_location": rental_record.start_location.id if rental_record.start_location else None,
            "is_active": rental_record.is_active
        }


        """
        an error is generated by the following code here
        AttributeError at /vehicles/rent_vehicle/
        'WSGIRequest' object has no attribute 'uesr'
        Request Method:	POST
        Request URL:	http://localhost:8000/vehicles/rent_vehicle/
        Django Version:	5.1.2
        Exception Type:	AttributeError
        Exception Value:	
        'WSGIRequest' object has no attribute 'uesr'
        """
        request.user.customerprofile.is_renting = True

        request.user.customerprofile.save()
        selected_vehicle.save()
        rental_record.save()
        return JsonResponse({'Vehicle rented successfully': selected_vehicle_json, 'Rental': rental_record_json})


def calculate_total_cost(distance_km, duration_hours):
    distance_rate = 1.5
    time_rate = 2.0

    total_cost = (distance_km * distance_rate) + (duration_hours * time_rate)
    return total_cost

@csrf_exempt
def return_vehicle(request):
    if not request.user.has_perm('users.return_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data["vehicle_id"]
            end_location_id = data["end_location_id"]
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

        try:
            selected_vehicle = models.Vehicle.objects.get(id=vehicle_id)
            rental_record = models.Rental.objects.get(vehicle=selected_vehicle, customer=request.user, is_active=True)
            end_location = models.StationLocation.objects.get(id=end_location_id)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)
        except models.Rental.DoesNotExist:
            return JsonResponse({'message': 'Active rental record not found for this vehicle and user'}, status=404)
        except models.StationLocation.DoesNotExist:
            return JsonResponse({'message': 'End location not found'}, status=404)

        # Update vehicle details
        selected_vehicle.station_id = end_location
        selected_vehicle.status = 'Available'
        selected_vehicle.battery_level = max(selected_vehicle.battery_level - 10, 0)

        # Calculate distance and time
        start_location = rental_record.start_location
        if start_location and end_location:
            start_coords = (start_location.latitude, start_location.longitude)
            end_coords = (end_location.latitude, end_location.longitude)
            distance_km = geodesic(start_coords, end_coords).km
        else:
            distance_km = 0

        duration = timezone.now() - rental_record.start_time
        duration_hours = duration.total_seconds() / 3600  # Convert duration to hours

        # Calculate total cost
        total_cost = calculate_total_cost(distance_km, duration_hours)

        # Update rental record
        rental_record.end_time = timezone.now()
        rental_record.end_location = end_location
        rental_record.total_cost = total_cost
        rental_record.is_active = False

        request.user.customerprofile.account_balance += Decimal(total_cost)
        request.user.customerprofile.is_renting = False


        rental_record_json = {
            "id": rental_record.id,
            "customer": rental_record.customer.id,
            "vehicle id": selected_vehicle.id,
            "start_time": rental_record.start_time.isoformat(),
            "end_time": rental_record.end_time.isoformat(),
            "start_location": start_location.id if start_location else None,
            "end_location": end_location.id,
            "distance_km": distance_km,
            "duration_hours": duration_hours,
            "total_cost": total_cost,
            "is_active": rental_record.is_active
        }


        selected_vehicle.save()
        rental_record.save()
        request.user.customerprofile.save()
        return JsonResponse({'message': 'Vehicle returned successfully', 'rental_record': rental_record_json})
