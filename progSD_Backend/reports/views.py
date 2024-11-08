from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from vehicles import models
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Count



def total_payments_per_location(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    
    try:
        # Optional: Get time range from query parameters (e.g., start_date, end_date)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        print(start_date)
        print(end_date)
        # Convert to datetime objects if provided
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # To include the entire end date

        
        # Start with the Payment model and apply filters based on date range
        payment_query = models.Payment.objects.values('rental__start_location__name') \
            .annotate(total_payment=Sum('amount'))

        # Apply date filters if both start_date and end_date are provided
        if start_date and end_date:
            payment_query = payment_query.filter(rental__start_time__gte=start_date, rental__end_time__lte=end_date)
        elif start_date:
            payment_query = payment_query.filter(rental__start_time__gte=start_date)
        elif end_date:
            payment_query = payment_query.filter(rental__end_time__lte=end_date)

        # Optionally, order by location name
        total_payments = payment_query.order_by('rental__start_location__name')

        # Format the result
        result = [
            {
                'location': entry['rental__start_location__name'],
                'total_payment': entry['total_payment']
            }
            for entry in total_payments
        ]
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


#2: Most Used Vehicle Types Over Time
def most_used_vehicle_types(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)
    
    try:
        # Optional: Get time range from query parameters (e.g., start_date, end_date)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        # Convert to datetime objects if provided
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # To include the entire end date

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
def most_popular_rental_locations(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        # Get start_date and end_date from the query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        # Convert string dates to datetime objects if provided
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to the past 30 days if no date range is provided
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        location_popularity = models.Rental.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).values('start_location__id', 'start_location__name', 'start_location__address') \
            .annotate(rental_count=Count('start_location')) \
            .order_by('-rental_count')

        result = []
        for entry in location_popularity:
            result.append({
                'location_id': entry['start_location__id'],
                'location_name': entry['start_location__name'],
                'location_address': entry['start_location__address'],
                'rental_count': entry['rental_count'],
            })

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
    

def most_popular_destination_locations(request):
    if not request.user.has_perm('users.generate_reports'):
        return JsonResponse({'message': 'Permission denied'}, status=403)

    try:
        # Get start_date and end_date from the query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Convert string dates to datetime objects if provided
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to the past 30 days if no date range is provided
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)


        location_popularity = models.Rental.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        ).values('end_location__id', 'end_location__name', 'end_location__address') \
            .annotate(destination_count=Count('end_location')) \
            .order_by('-destination_count')

        result = []
        for entry in location_popularity:
            result.append({
                'location_id': entry['end_location__id'],
                'location_name': entry['end_location__name'],
                'location_address': entry['end_location__address'],
                'destination_count': entry['destination_count'],
            })

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
    

