from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def register_view(request):
    return HttpResponse('Registration is here')