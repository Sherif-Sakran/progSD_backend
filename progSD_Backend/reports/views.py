from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from vehicles import models
from vehicles import models as vmodels
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Count, Q


from django.db.models import Sum
from django.utils.timezone import make_aware
import datetime
from django.db.models import Avg, F, ExpressionWrapper, fields

@csrf_exempt
def total_payments_per_location(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    
    try:
        # Get and parse date/time range from query parameters
        start_date_str = request.GET.get('start_date')
        start_time_str = request.GET.get('start_time')
        end_date_str = request.GET.get('end_date')
        end_time_str = request.GET.get('end_time')
        
        if start_date_str and start_time_str:
            start_datetime = make_aware(datetime.datetime.strptime(f"{start_date_str} {start_time_str}", '%Y-%m-%d %H:%M:%S'))
        else:
            start_datetime = None

        if end_date_str and end_time_str:
            end_datetime = make_aware(datetime.datetime.strptime(f"{end_date_str} {end_time_str}", '%Y-%m-%d %H:%M:%S'))
        else:
            end_datetime = None

        # Query all station locations
        all_locations = vmodels.StationLocation.objects.values('id', 'name')

        # Fetch total payments for each location with rentals in the time range
        payment_query = vmodels.Payment.objects.select_related('rental__start_location') \
            .values('rental__start_location__id') \
            .annotate(total_payment=Sum('amount'))
        
        # Apply date filters if specified
        if start_datetime:
            payment_query = payment_query.filter(rental__start_time__gte=start_datetime)
        if end_datetime:
            payment_query = payment_query.filter(rental__end_time__lte=end_datetime)

        payment_dict = {entry['rental__start_location__id']: entry['total_payment'] for entry in payment_query}

        result = [
            {
                'location': location['name'],
                'total_payment': payment_dict.get(location['id'], 0.0)
            }
            for location in all_locations
        ]
        
        result.sort(key=lambda x: x['total_payment'], reverse=True)

        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


#2: Most Used Vehicle Types Over Time
@csrf_exempt
def most_used_vehicle_types(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    
    try:
        start_date_str = request.GET.get('start_date', None)
        start_time_str = request.GET.get('start_time', None)
        end_date_str = request.GET.get('end_date', None)
        end_time_str = request.GET.get('end_time', None)

        start_date_str = start_date_str + ' ' + start_time_str
        end_date_str = end_date_str + ' ' + end_time_str

        # Convert to datetime objects if provided, including time
        if start_date_str:
            # The expected format: 'YYYY-MM-DD HH:MM:SS'
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            start_date = None
        
        if end_date_str:
            # The expected format: 'YYYY-MM-DD HH:MM:SS'
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)  # To include the entire end date
        else:
            end_date = None

        # Start with the Rental model and join with the Vehicle model
        vehicle_usage_query = models.Rental.objects.values('vehicle__type') \
            .annotate(vehicle_count=Count('vehicle'))  # Count how many times each vehicle type was rented

        # Apply date filters if both start_date and end_date are provided
        if start_date and end_date:
            vehicle_usage_query = vehicle_usage_query.filter(start_time__gte=start_date, end_time__lte=end_date)
        elif start_date:
            vehicle_usage_query = vehicle_usage_query.filter(start_time__gte=start_date)
        elif end_date:
            vehicle_usage_query = vehicle_usage_query.filter(end_time__lte=end_date)

        # Optionally, order by vehicle count (descending)
        most_used_vehicle_types = vehicle_usage_query.order_by('-vehicle_count')

        # Format the result
        result = [
            {
                'vehicle_type': entry['vehicle__type'],
                'usage_count': entry['vehicle_count']
            }
            for entry in most_used_vehicle_types
        ]
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


#3: Vehicles Currently in Use
@csrf_exempt
def vehicles_currently_in_use(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        # Query to get vehicles that are currently in use (active rentals)
        active_rentals = models.Rental.objects.filter(is_active=True, end_time__isnull=True)  # End time is null for active rentals

        # Retrieve the vehicle details for the currently rented vehicles
        vehicles_in_use = active_rentals.values('vehicle__id', 'vehicle__type', 'vehicle__make', 'vehicle__model')

        # Format the result into a list of dictionaries
        result = [
            {
                'vehicle_id': entry['vehicle__id'],
                'vehicle_type': entry['vehicle__type'],
                'vehicle_make': entry['vehicle__make'],
                'vehicle_model': entry['vehicle__model'],
            }
            for entry in vehicles_in_use
        ]

        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
 
#4: Most Popular Rental Locations
@csrf_exempt
def most_popular_rental_locations(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        start_date_str = request.GET.get('start_date', None)
        start_time_str = request.GET.get('start_time', None)
        end_date_str = request.GET.get('end_date', None)
        end_time_str = request.GET.get('end_time', None)

        start_date_str = start_date_str + ' ' + start_time_str
        end_date_str = end_date_str + ' ' + end_time_str

        # Convert to datetime objects with time if provided
        if start_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            start_date = None
        
        if end_date_str:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)  # To include the entire end date
        else:
            end_date = None

        # Default to the past 30 days if no date range is provided
        if not start_date:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        # Query for popular rental locations within the date range
        location_popularity = models.Rental.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).values('start_location__id', 'start_location__name', 'start_location__address') \
            .annotate(rental_count=Count('start_location')) \
            .order_by('-rental_count')

        # Format the result
        result = [
            {
                'location_id': entry['start_location__id'],
                'location_name': entry['start_location__name'],
                'location_address': entry['start_location__address'],
                'rental_count': entry['rental_count'],
            }
            for entry in location_popularity
        ]

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


@csrf_exempt
def most_popular_destination_locations(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        start_date_str = request.GET.get('start_date', None)
        start_time_str = request.GET.get('start_time', None)
        end_date_str = request.GET.get('end_date', None)
        end_time_str = request.GET.get('end_time', None)

        start_date_str = start_date_str + ' ' + start_time_str
        end_date_str = end_date_str + ' ' + end_time_str

        # Convert to datetime objects with time if provided
        if start_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            start_date = None
        
        if end_date_str:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)  # To include the entire end date
        else:
            end_date = None

        # Default to the past 30 days if no date range is provided
        if not start_date:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        # Query for popular destination locations within the date range
        location_popularity = models.Rental.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).values('end_location__id', 'end_location__name', 'end_location__address') \
            .annotate(destination_count=Count('end_location')) \
            .order_by('-destination_count')

        # Format the result
        result = [
            {
                'location_id': entry['end_location__id'],
                'location_name': entry['end_location__name'],
                'location_address': entry['end_location__address'],
                'destination_count': entry['destination_count'],
            }
            for entry in location_popularity
        ]

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
    

def number_of_vehicles(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        station_id = request.GET.get('station_id', None)
        vehicle_type = request.GET.get('vehicle_type', None)

        vehicle_query = vmodels.StationLocation.objects.values('id', 'name') \
            .annotate(vehicle_count=Count('vehicle'))

        if station_id:
            vehicle_query = vehicle_query.filter(id=station_id)
        if vehicle_type:
            vehicle_query = vehicle_query.filter(vehicle__type=vehicle_type)

        vehicle_counts = vehicle_query.order_by('name')

        result = [
            {
                'station_id': entry['id'],
                'station_name': entry['name'],
                'vehicle_count': entry['vehicle_count']
            }
            for entry in vehicle_counts
        ]

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


def vehicle_rental_average(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        # Get date and time range from query parameters
        start_date_str = request.GET.get('start_date', None)
        start_time_str = request.GET.get('start_time', None)
        end_date_str = request.GET.get('end_date', None)
        end_time_str = request.GET.get('end_time', None)

        # Combine date and time strings
        if start_date_str and start_time_str:
            start_date_str = f"{start_date_str} {start_time_str}"
        if end_date_str and end_time_str:
            end_date_str = f"{end_date_str} {end_time_str}"

        # Convert strings to datetime objects
        if start_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            start_date = None

        if end_date_str:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)  # To include the entire end date
        else:
            end_date = None

        # Filter Rentals with valid end_time and calculate the duration
        rental_durations = vmodels.Rental.objects.exclude(end_time__isnull=True) \
            .annotate(
                duration=ExpressionWrapper(
                    F('end_time') - F('start_time'), output_field=fields.DurationField()
                )
            ).select_related('vehicle')

        # Apply date filters if provided
        if start_date and end_date:
            rental_durations = rental_durations.filter(start_time__gte=start_date, end_time__lte=end_date)
        elif start_date:
            rental_durations = rental_durations.filter(start_time__gte=start_date)
        elif end_date:
            rental_durations = rental_durations.filter(end_time__lte=end_date)

        # Calculate average duration per vehicle type
        average_durations = rental_durations.values('vehicle__type') \
            .annotate(average_duration=Avg('duration'))

        # Format the result as hours and minutes for readability
        result = [
            {
                'vehicle_type': entry['vehicle__type'],
                'average_duration': str(timedelta(seconds=entry['average_duration'].total_seconds()))
            }
            for entry in average_durations
        ]

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


def most_reported_vehicles(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        start_date_str = request.GET.get('start_date', None)
        start_time_str = request.GET.get('start_time', None)
        end_date_str = request.GET.get('end_date', None)
        end_time_str = request.GET.get('end_time', None)

        if start_date_str and start_time_str:
            start_datetime_str = f"{start_date_str} {start_time_str}"
            start_datetime = timezone.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
        else:
            start_datetime = None
        
        if end_date_str and end_time_str:
            end_datetime_str = f"{end_date_str} {end_time_str}"
            end_datetime = timezone.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S') + timedelta(days=1)  # To include the entire end date
        else:
            end_datetime = None

        reported_vehicles = vmodels.CustomerReportedDefects.objects.values('vehicle__type') \
            .annotate(
                total_reports=Count('id'),
                defective_reports=Count('id', filter=Q(found_defective=True)),
                non_defective_reports=Count('id', filter=Q(found_defective=False))
            )

        # Apply date range filters if both start_datetime and end_datetime are provided
        if start_datetime and end_datetime:
            reported_vehicles = reported_vehicles.filter(report_date__gte=start_datetime, report_date__lte=end_datetime)
        elif start_datetime:
            reported_vehicles = reported_vehicles.filter(report_date__gte=start_datetime)
        elif end_datetime:
            reported_vehicles = reported_vehicles.filter(report_date__lte=end_datetime)

        # Format the result
        result = [
            {
                'vehicle_type': entry['vehicle__type'],
                'total_reports': entry['total_reports'],
                'defective_reports': entry['defective_reports'],
                'non_defective_reports': entry['non_defective_reports']
            }
            for entry in reported_vehicles
        ]

        # Return the formatted result as a JSON response
        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
