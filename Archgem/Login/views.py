from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
import json

# only basic login supported for now
@csrf_exempt
def index(request:HttpRequest):
    data = json.loads(request.body)
    authToken = data.get('token')
    if authToken:
        # Validate the token and retrieve the user
        token = Token.objects.get(key=token)
        user = token.user
        login(request, user)
        print("SUCCESS, LOGGED IN WITH TOKEN")
        return JsonResponse({'token': str(token.key)}, status=200)
    elif request.method == 'POST':
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