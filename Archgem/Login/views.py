from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
# api/views.py
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.authtoken.models import Token
from django.middleware.csrf import get_token
import json

# only basic login supported for now
@csrf_exempt
def index(request:HttpRequest):
    print("HERE")
    print(request.headers)
    if request.method == 'POST':
        # Parsing username and password from the request body
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        # Authenticating the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # The credentials are correct
            login(request, user)  # Initiating a user session
            print("SUCCESS, LOGGED IN")
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': str(token.key)}, status=200)
        else:
            # Incorrect credentials
            return HttpResponse(status=401)

    return HttpResponse("Method not allowed", status=405)