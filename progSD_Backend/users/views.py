from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.http import JsonResponse



# Create your views here.
def register_view(request):
    return HttpResponse('Registration is here')

def login_view(request):
    return HttpResponse('Login')

def fetch_data_vehicles(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vehicles")
        rows = cursor.fetchall()
    return JsonResponse({'data': rows})