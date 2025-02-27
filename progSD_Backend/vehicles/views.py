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
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


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
        except models.StationLocation.DoesNotExist:
            return JsonResponse({'message': 'Station location with the given ID does not exist.'}, status=400)


def list_locations(request):
    print('list locations function call')
    current_locations = models.StationLocation.objects.all()
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
    return JsonResponse(current_locations_json, safe=False)


def list_vehicles(request):
    print('list vehicles function call')
    current_vehicles = models.Vehicle.objects.all()
    current_vehicles_json = []
    for vehicle in current_vehicles:
        current_vehicles_json.append(
            {
                "id": vehicle.id,
                "type": vehicle.type,
                "make": vehicle.make,
                "model": vehicle.model,
                "battery_level": vehicle.battery_level,
                "status": vehicle.status,
                "station_id": vehicle.station_id.id if vehicle.station_id else None,
                "location_latitude": vehicle.station_id.latitude if vehicle.station_id else None,
                "location_longitude": vehicle.station_id.longitude if vehicle.station_id else None,
                "last_maintenance_date": vehicle.last_maintenance_date.isoformat(),
                "is_defective": vehicle.is_defective,
            }
        )
    return JsonResponse(current_vehicles_json, safe=False)


@csrf_exempt
def list_available_vehicles_at(request):
    if request.method == 'POST':
        try:
            location_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        print('list available vehicles at a certain location')
        current_vehicles = models.Vehicle.objects.filter(status='Available', station_id=location_json["location_id"])
        current_vehicles_json = []
        for vehicle in current_vehicles:
            current_vehicles_json.append(
                {
                    "id": vehicle.id,
                    "type": vehicle.type,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "battery_level": vehicle.battery_level,
                    "status": vehicle.status,
                    "station_id": vehicle.station_id.id if vehicle.station_id else None,
                    "last_maintenance_date": vehicle.last_maintenance_date.isoformat(),
                    "is_defective": vehicle.is_defective,
                }
            )
        return JsonResponse(current_vehicles_json, safe=False)


@csrf_exempt
def fetch_vehicles(request):
    if not request.user.has_perm('users.rent_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            filters = {}

            vehicle_type = data.get('type')
            status = data.get('status')
            station_id = data.get('station_id')
            min_battery_level = data.get('min_battery_level')
            max_battery_level = data.get('max_battery_level')
            is_defective = data.get('is_defective', None)
            min_last_maintenance_date = data.get('min_last_maintenance_date')
            max_last_maintenance_date = data.get('max_last_maintenance_date')

            if vehicle_type:
                filters['type'] = vehicle_type
            if status:
                filters['status'] = status
            if station_id:
                filters['station_id'] = station_id
            if is_defective is not None:
                filters['is_defective'] = is_defective
            

            if min_battery_level is not None:
                filters['battery_level__gte'] = min_battery_level
            if max_battery_level is not None:
                filters['battery_level__lte'] = max_battery_level

            if min_last_maintenance_date:
                parsed_min_date = parse_date(min_last_maintenance_date)
                if parsed_min_date:
                    filters['last_maintenance_date__gte'] = parsed_min_date
            if max_last_maintenance_date:
                parsed_max_date = parse_date(max_last_maintenance_date)
                if parsed_max_date:
                    filters['last_maintenance_date__lte'] = parsed_max_date

            vehicles = models.Vehicle.objects.filter(**filters)

            # Format the response data
            vehicle_data = [
                {
                    "id": vehicle.id,
                    "type": vehicle.type,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "battery_level": vehicle.battery_level,
                    "status": vehicle.status,
                    "station_id": vehicle.station_id.id if vehicle.station_id else None,
                    "last_maintenance_date": vehicle.last_maintenance_date,
                    "is_defective": vehicle.is_defective,
                }
                for vehicle in vehicles
            ]

            return JsonResponse(vehicle_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def rent_vehicle(request):
    if not request.user.has_perm('users.rent_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)


    if request.method == 'POST':
        if request.user.customerprofile.is_renting:
            return JsonResponse({'message': 'You cannot rent more than once at the same time'}, status=400)

        try:
            print('received request')
            vehicle_id_JSON = json.loads(request.body)
            print('received car id', vehicle_id_JSON["id"])
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        selected_vehicle = models.Vehicle.objects.filter(id=vehicle_id_JSON["id"])[0]
        
        User = get_user_model()
        
        selected_vehicle_json = {
            "id": selected_vehicle.id,
            "type": selected_vehicle.type,
            "make": selected_vehicle.make,
            "model": selected_vehicle.model,
            "battery_level": selected_vehicle.battery_level,
            "status": selected_vehicle.status,
            "station_location": selected_vehicle.station_id.id if selected_vehicle.station_id else None,
            "last_maintenance_date": selected_vehicle.last_maintenance_date.isoformat(),
            "is_defective": selected_vehicle.is_defective,
        }
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

        selected_vehicle.status = 'Rented'
        selected_vehicle.station_id = None

        request.user.customerprofile.is_renting = True

        request.user.customerprofile.save()
        selected_vehicle.save()
        rental_record.save()
        return JsonResponse({'message': 'Vehicle rented successfully', 'Rental': rental_record_json})


def calculate_total_cost(distance_km, duration_hours, vehicle_type, discount):
    distance_rate = 1.5
    time_rate = 2.0
    max_discount_amount = 5

    factor = {
        'Electric Car': 1.5,     
        'Electric Scooter': 0.8, 
        'Electric Bike': 0.5     
    }

    total_cost = ((distance_km * distance_rate) + (duration_hours * time_rate)) * factor[vehicle_type]
    print('cost before discount: ', total_cost)
    
    discount = float(discount)
    
    
    total_cost = max(total_cost*(1-discount), total_cost-max_discount_amount)
    
    print('cost after discount: ', total_cost)
    return max(total_cost, 2.0)


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


        applied_discount = request.user.customerprofile.discount
        discount_expirty_date = request.user.customerprofile.discount_valid_until
        if discount_expirty_date and discount_expirty_date < timezone.now():
            applied_discount
        
        total_cost = calculate_total_cost(distance_km, duration_hours, selected_vehicle.type, applied_discount)

        # Update rental record
        rental_record.end_time = timezone.now()
        rental_record.end_location = end_location
        rental_record.total_cost = total_cost
        rental_record.is_active = False

        request.user.customerprofile.charges += Decimal(total_cost)
        request.user.customerprofile.is_renting = False

        vehicle_return_location = models.VehicleLocation(
            vehicle_id = selected_vehicle,
            longitude=end_location.longitude,
            latitude=end_location.latitude
        )

        vehicle_return_location.save()

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

@csrf_exempt
def report_defective_vehicle(request):
    if not request.user.has_perm('users.report_defective_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data["vehicle_id"]
            description = data.get("description", "")
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

        try:
            selected_vehicle = models.Vehicle.objects.get(id=vehicle_id)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)

        active_rental = models.Rental.objects.filter(
            vehicle=selected_vehicle,
            customer=request.user,
            is_active=True
        ).first()

        recent_rental = models.Rental.objects.filter(
            vehicle=selected_vehicle,
            customer=request.user,
            start_time__gte=timezone.now() - timedelta(hours=24)
        ).first()

        if not active_rental and not recent_rental:
            return JsonResponse({'message': 'You can only report vehicles you are renting or rented in the last 24 hours'}, status=403)

        defect_report = models.CustomerReportedDefects.objects.create(
            vehicle=selected_vehicle,
            reported_by=request.user,
            report_date=timezone.now(),
            description=description
        )

        defect_report_json = {
            "id": defect_report.id,
            "vehicle": selected_vehicle.id,
            "reported_by": request.user.id,
            "report_date": defect_report.report_date.isoformat(),
            "description": defect_report.description
        }

        return JsonResponse({'message': 'Vehicle reported as defective successfully', 'defect_report': defect_report_json})
    

def get_defect_reports(request):
    if not request.user.has_perm('users.repair_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method == 'GET':
        # Filter reports made by the current user
        defect_reports = models.CustomerReportedDefects.objects.all()
        
        # Serialize the reports
        reports_list = [
            {
                "id": report.id,
                "vehicle": report.vehicle.id,
                "vehicle_type": report.vehicle.type,
                "reported_by": report.reported_by.id,
                "report_date": report.report_date.isoformat(),
                "description": report.description,
                "found_defective": report.found_defective,
                "confirmed_date": report.confirmed_date.isoformat() if report.confirmed_date else None,
                "defect_fixed": report.defect_fixed
            }
            for report in defect_reports
        ]
        
        return JsonResponse(reports_list, safe=False)
    
    return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def confirm_defective_vehicle(request):
    if not request.user.has_perm('users.repair_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            defect_id = data.get("defect_id")
            vehicle_found_defective = data.get("found_defective")
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid request data'}, status=400)

        try:
            defect_report = models.CustomerReportedDefects.objects.get(id=defect_id)
            selected_vehicle = defect_report.vehicle
        except models.CustomerReportedDefects.DoesNotExist:
            return JsonResponse({'message': 'Defect report not found'}, status=404)

        selected_vehicle.status = 'Defective'
        selected_vehicle.is_defective=True

        defect_report.found_defective = vehicle_found_defective
        defect_report.confirmed_date = timezone.now()
        
        selected_vehicle.save()
        defect_report.save()
        return JsonResponse({'message': '    confirmed successfully'})

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def repair_vehicle(request):
    # Check for repair_vehicle permission
    if not request.user.has_perm('users.repair_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        # Parse request data
        data = json.loads(request.body)
        defect_id = data.get("defect_id")
        notes = data.get("notes", "")
        repair_cost = data.get("repair_cost", 0.00)
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid request data'}, status=400)

    try:
        # Fetch defect report and associated vehicle
        defect_report = models.CustomerReportedDefects.objects.get(id=defect_id)
        selected_vehicle = defect_report.vehicle
    except models.CustomerReportedDefects.DoesNotExist:
        return JsonResponse({'message': 'Defect report not found'}, status=404)

    defect_report.defect_fixed = True
    defect_report.save()
    
    # Log repair details in RepairsLog
    repair_record = models.RepairsLog.objects.create(
        defect=defect_report,
        operator=request.user,
        repair_date=timezone.now(),
        notes=notes,
        repair_cost=repair_cost
    )

    # Prepare JSON response
    repair_log_json = {
        "id": repair_record.id,
        "defect": defect_id,
        "operator": request.user.id,
        "repair_date": repair_record.repair_date.isoformat(),
        "notes": repair_record.notes,
        "repair_cost": str(repair_record.repair_cost)
    }

    return JsonResponse({
        'message': 'Vehicle repair logged successfully',
        'repair_log': repair_log_json
    })


@csrf_exempt
def list_low_battery_vehicles(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            battery_threshold = data.get("battery_level")
            vehicle_type = data.get("type")

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid request data'}, status=400)

        try:
            battery_threshold = int(battery_threshold)  
        except ValueError:
            return JsonResponse({'message': 'Invalid battery level threshold'}, status=400)

        # Filter vehicles based on battery level and type
        low_battery_vehicles = models.Vehicle.objects.filter(
            battery_level__lte=battery_threshold,
            type=vehicle_type
        )

        # Prepare the response data
        vehicles_list = [{
            "id": vehicle.id,
            "battery_level": vehicle.battery_level,
            "type": vehicle.type,
            "make": vehicle.make,
            "model": vehicle.model,
            "status": vehicle.status
        } for vehicle in low_battery_vehicles]

        return JsonResponse(vehicles_list, safe=False)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@csrf_exempt
def charge_vehicle(request):
    if not request.user.has_perm('users.charge_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data.get("vehicle_id")
            charge_up_to = data.get("charge_up_to")
            notes = data.get("notes", "")
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid request data'}, status=400)

        try:
            selected_vehicle = models.Vehicle.objects.get(id=vehicle_id)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)

        original_battery_level = selected_vehicle.battery_level

        selected_vehicle.battery_level = charge_up_to

        charge_record = models.ChargesLog.objects.create(
            vehicle=selected_vehicle,
            operator=request.user,
            charge_date=timezone.now(),
            charge_up_to=charge_up_to,
            original_battery_level=original_battery_level,
            notes=notes
        )
        charge_record_json = {
            "id": charge_record.id,
            "vehicle": selected_vehicle.id,
            "operator": request.user.id,
            "charge_date": charge_record.charge_date.isoformat(),
            "charge_up_to": charge_record.charge_up_to,
            "original_battery_level": charge_record.original_battery_level,
            "notes": charge_record.notes
        }
        selected_vehicle.save()
        charge_record.save()
        # Prepare JSON response with charge details

        return JsonResponse({'message': 'Vehicle charged successfully', 'charge_record': charge_record_json})

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def move_vehicle(request):
    if not request.user.has_perm('users.move_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data["vehicle_id"]
            move_to_station = data["move_to_station"]
            station_id = data.get("station_id")
            latitude = data.get("latitude")
            longitude = data.get("longitude")
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

        try:
            selected_vehicle = models.Vehicle.objects.get(id=vehicle_id)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)
        
        rental_record = models.Rental.objects.filter(vehicle=selected_vehicle, is_active=True)
        
        if rental_record:
            return JsonResponse({'message': 'You cannot move the vehicle while it is being rented'}, status=404)

        if move_to_station:
            if not station_id:
                return JsonResponse({'message': 'Station ID is required when moving to a station'}, status=400)
            
            try:
                destination_station = models.StationLocation.objects.get(id=station_id)
            except models.StationLocation.DoesNotExist:
                return JsonResponse({'message': 'Station not found'}, status=404)
            
            selected_vehicle.station_id = destination_station
            selected_vehicle.save()
            message = 'Vehicle location updated to station successfully'

        else:
            if latitude is None or longitude is None:
                return JsonResponse({'message': 'Latitude and longitude are required when moving to a non-station location'}, status=400)
            
            selected_vehicle.station_id = None
            selected_vehicle.save()

            models.VehicleLocation.objects.create(
                vehicle_id=selected_vehicle,
                timestamp=timezone.now(),
                latitude=latitude,
                longitude=longitude
            )
            message = 'Vehicle location updated to the specified coordinates successfully'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt 
def update_vehicle_location(request):
    if not request.user.has_perm('users.rent_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            vehicle_id = data["vehicle_id"]
            latitude = data["latitude"]
            longitude = data["longitude"]
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

        try:
            selected_vehicle = models.Vehicle.objects.get(id=vehicle_id)
            rental_record = models.Rental.objects.get(vehicle=selected_vehicle, customer=request.user, is_active=True)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)
        except models.Rental.DoesNotExist:
            return JsonResponse({'message': 'Active rental record not found for this vehicle and user'}, status=404)
        
        models.VehicleLocation.objects.create(
            vehicle_id=rental_record.vehicle,
            timestamp=timezone.now(),
            latitude=latitude,
            longitude=longitude
        )

        return JsonResponse({'message': 'Vehicle location updated successfully'})

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def track_vehicle(request):
    if not request.user.has_perm('users.track_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':        
        try:
            data = json.loads(request.body)
            vehicle_id = data["vehicle_id"]
            time_range = data.get("time_range", None)
            max_records = data.get("max_records", 10)

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

        try:
            vehicle = models.Vehicle.objects.get(id=vehicle_id)
        except models.Vehicle.DoesNotExist:
            return JsonResponse({'message': 'Vehicle not found'}, status=404)

        try:
            if time_range:
                hours = int(time_range)
                since_time = timezone.now() - timedelta(hours=hours)
                locations = models.VehicleLocation.objects.filter(
                    vehicle_id=vehicle, timestamp__gte=since_time
                ).order_by('-timestamp')[:max_records]
            else:
                locations = models.VehicleLocation.objects.filter(
                    vehicle_id=vehicle
                ).order_by('-timestamp')[:max_records]
        except ValueError:
            return JsonResponse({'message': 'Invalid time range format'}, status=400)

        location_data = [
            {
                "timestamp": loc.timestamp,
                "latitude": loc.latitude,
                "longitude": loc.longitude
            }
            for loc in locations
        ]

        return JsonResponse({'vehicle_id': vehicle_id, 'locations': location_data})
    return JsonResponse({'message': 'Invalid request method'}, status=405)


def validate_bank_card(card_number, passcode):
    return True


@csrf_exempt
def pay_charges(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        payment_method = data.get("payment_method", "Account")
        card_number = data.get("card_number", None)
        card_passcode = data.get("card_passcode", None)
        coupon = data.get("coupon", None)

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

    try:
        customer_profile = request.user.customerprofile

        if customer_profile.is_renting:
            return JsonResponse({'message': 'Your rental has not finished yet. '}, status=400)

        last_rental = models.Rental.objects.filter(customer=request.user, is_active=False).order_by('-end_time').first()
        print(last_rental)
        if not last_rental:
            return JsonResponse({'message': 'No unpaid rentals found.'}, status=404)
        amount_due = last_rental.total_cost
        if payment_method == "Account":    
            if customer_profile.account_balance < amount_due:
                return JsonResponse({'message': 'Insufficient account balance.'}, status=400)

        if payment_method == "Credit Card" or payment_method == "Debit Card" or payment_method == "PayPal":
            if not card_number or not card_passcode:
                return JsonResponse({'message': 'Card details were not provided.'}, status=400)
            
            print(f'validating {card_number} with hashed pascode {card_passcode}')
            valid_credentials = validate_bank_card(card_number, card_passcode)
            if not valid_credentials:
                return JsonResponse({'message': 'Credentials are not valid.'}, status=404)
            print(f'Successful validation')


        last_payment = models.Payment.objects.filter(rental=last_rental).first()
        
        if last_payment:
            return JsonResponse({'message': f'Payment has already done and processed before'})

        customer_profile.charges -= Decimal(amount_due)
        coupon_row = None
        if coupon:
            # check if the coupon is valid
            coupon_row = models.Coupon.objects.filter(code=coupon).first()
            if not coupon_row:
                return JsonResponse({'message': 'Coupon not found'}, status=404)
            if coupon_row.valid_until <= timezone.now().date():
                return JsonResponse({'message': 'Coupon expired'}, status=404)
            
            
            uses_count = models.CouponUse.objects.filter(coupon=coupon_row, user=request.user).count()
            if uses_count >= coupon_row.max_use:
                return JsonResponse({'message': 'Coupon has been used the maximum number of times.'}, status=404)
            
            amount_due_after_coupon = float(amount_due)*(1-float(coupon_row.discount))
            price_if_max_coupon = float(amount_due) - float(coupon_row.max_discount_amount)
            amount_due = max(amount_due_after_coupon, price_if_max_coupon)


        if payment_method == "Account":    
            customer_profile.account_balance -= Decimal(amount_due)
        
        # coupon as a fk field is to be added to the payments table

        customer_profile.save()
        models.CouponUse.objects.create(
                        coupon=coupon_row,
                        user=request.user,
                        discount_applied=Decimal(min(float(coupon_row.discount)*float(amount_due), float(coupon_row.max_discount_amount)))
                    )
        models.Payment.objects.create(
            customer=request.user,
            rental=last_rental,
            coupon=coupon_row,
            amount=Decimal(amount_due),
            payment_method=payment_method,
            timestamp=timezone.now()
        )
        json_return = {'message': f'Payment successful through {payment_method}', 'amount': amount_due}
        if coupon_row:
            json_return["coupon"] = coupon_row.code
        if customer_profile.discount != Decimal(0.0):
            json_return["discount"] = customer_profile.discount
            json_return["discount expiry date"] = customer_profile.discount_valid_until

        return JsonResponse(json_return)

    except request.user.customerprofile.DoesNotExist:
        return JsonResponse({'message': 'Customer profile not found.'}, status=404)


@csrf_exempt
def charge_account(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        amount_to_pay = data["amount_to_pay"]
        payment_method = data["payment_method"]
        card_number = data["card_number"]
        card_passcode = make_password(data["card_passcode"])

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

    try:
        customer_profile = request.user.customerprofile

        print(f'validating {card_number} with hashed pascode {card_passcode}')
        valid_credentials = validate_bank_card(card_number, card_passcode)
        if not valid_credentials:
            return JsonResponse({'message': 'Credentials are not valid.'}, status=404)
        print(f'Successful validation')
        
        customer_profile.account_balance += Decimal(amount_to_pay)
        customer_profile.save()

        return JsonResponse({'message': f'Payment successful through {payment_method}', 'account balance': customer_profile.account_balance})

    except request.user.customerprofile.DoesNotExist:
        return JsonResponse({'message': 'Customer profile not found.'}, status=404)


@csrf_exempt
def request_discount(request):
    if not request.user.has_perm('users.request_discount') and not request.user.has_perm('users.rent_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        student_id_number = data["student_id_number"]
        institution = data["institution"]
        student_email = data["student_email"]
        id_valid_until = data["id_valid_until"]

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

    try:
        # Assuming request.user is a logged-in user
        customer = request.user

        # Create a new DiscountRequest entry
        discount_request = models.DiscountRequests.objects.create(
            customer=customer,
            student_id_number=student_id_number,
            institution=institution,
            student_email=student_email,
            id_valid_until=id_valid_until,
        )

        return JsonResponse({
            'message': 'Discount request created successfully',
            'request_id': discount_request.id,
            'student_id_number': discount_request.student_id_number,
            'institution': discount_request.institution,
            'student_email': discount_request.student_email,
            'id_valid_until': discount_request.id_valid_until
        }, status=201)

    except request.user.customerprofile.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=404)


def get_unverified_requests(request):
    if not request.user.has_perm('users.verify_requests') and not request.user.has_perm('users.track_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method != 'GET':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    unverified_requests = models.DiscountRequests.objects.filter(confirmed_date__isnull=True)
    
    requests_data = [
        {
            'id': request.id,
            'customer_id': request.customer.id,
            'student_id_number': request.student_id_number,
            'id_valid_until': request.id_valid_until,
            'institution': request.institution,
            'request_date': request.request_date,
            'response_by_operator': request.response_by_operator,
            'is_verified': request.is_verified,
        }
        for request in unverified_requests
    ]

    return JsonResponse(requests_data, safe=False)


@csrf_exempt
def verify_discount_request(request):
    if not request.user.has_perm('users.verify_requests') and not request.user.has_perm('users.track_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        request_id = data["request_id"]
        is_approved = data["is_approved"]
        response_by_operator = data.get("response_by_operator", "")

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)

    try:
        # Find the discount request by ID
        discount_request = models.DiscountRequests.objects.get(id=request_id)
        
        if  is_approved:
            discount_request.is_verified = True
            discount_request.confirmed_date = timezone.now()
            discount_request.response_by_operator = response_by_operator
            discount_request.save()
            
            # Update customer's discount in CustomerProfile
            customer_profile = discount_request.customer.customerprofile
            customer_profile.discount = 0.1
            customer_profile.discount_valid_until = discount_request.id_valid_until
            customer_profile.save()

            return JsonResponse({'message': 'Discount request accepted and discount applied', 'discount': customer_profile.discount})

        else:
            # Just update response_by_operator
            discount_request.response_by_operator = response_by_operator
            discount_request.save()

            return JsonResponse({'message': 'Discount request rejected', 'response_by_operator': response_by_operator})

    except models.DiscountRequests.DoesNotExist:
        return JsonResponse({'message': 'Discount request not found'}, status=404)
    
    except request.user.customerprofile.DoesNotExist:
        return JsonResponse({'message': 'Customer profile not found.'}, status=404)


@csrf_exempt
def add_partner(request):
    if not request.user.has_perm('users.add_partners') and not request.user.has_perm('users.move_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data["name"]
        category = data["category"]
        joined_date=data.get("joined_date", timezone.now())

        if category not in ['gold', 'silver', 'platinum']:
            return JsonResponse({'message': 'Invalid category'}, status=400)

        partner = models.Partner.objects.create(
            name=name,
            category=category,
            joined_date=joined_date
        )

        return JsonResponse({
            'message': 'Partner added successfully',
            'partner_id': partner.id,
            'name': partner.name,
            'category': partner.category
        }, status=201)

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)


@csrf_exempt
def add_coupon(request):
    if not request.user.has_perm('users.add_partners') and not request.user.has_perm('users.move_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data["code"]
        issued_by_id = data["issued_by"]
        valid_until = data["valid_until"]
        discount = data["discount"]
        max_discount_amount = data["max_discount_amount"]
        max_use = data.get("max_use", 1)
        try:
            issued_by = models.Partner.objects.get(id=issued_by_id)
        except models.Partner.DoesNotExist:
            return JsonResponse({'message': 'Partner not found'}, status=404)

        if max_use == "unlimited":
            max_use = 1000
        coupon = models.Coupon.objects.create(
            code=code,
            issued_by=issued_by,
            valid_until=valid_until,
            discount=discount,
            max_discount_amount=max_discount_amount,
            max_use=max_use
        )

        return JsonResponse({
            'message': 'Coupon added successfully',
            'coupon_id': coupon.id,
            'code': coupon.code,
            'issued_by': coupon.issued_by.name,
            'valid_until': coupon.valid_until,
            'discount': coupon.discount,
            'max_discount_amount': coupon.max_discount_amount,
            'max_use': coupon.max_use
        }, status=201)

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'message': 'Invalid JSON or missing parameters'}, status=400)
    except ValueError:
        return JsonResponse({'message': 'Invalid data types'}, status=400)


@csrf_exempt
def list_partners(request):
    if not request.user.has_perm('users.add_partners') and not request.user.has_perm('users.move_vehicle'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        partners = models.Partner.objects.all()

        partner_data = partners.values('id', 'name', 'joined_date', 'category')

        result = [
            {
                'id': entry['id'],
                'name': entry['name'],
                'joined_date': entry['joined_date'],
                'category': entry['category'],
            }
            for entry in partner_data
        ]

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
