from django.http import HttpResponse
from django.http import HttpRequest
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# Create your views here.

def index(request:HttpRequest):
    if request.method == "POST":
        print(request.body.decode("utf-8"))
    
    

    return HttpResponse("Hello, world. You're at the Login index." + request.body.decode("utf-8"))