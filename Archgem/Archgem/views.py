from django.http import HttpResponse
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token

#perform series of initialization tasks

def init(request:HttpRequest):
    #get csrf token
    if request.method == "GET":
        return get_token()
    else:
        return HttpResponse("Error: GET request required")