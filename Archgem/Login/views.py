from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
import json
import django
# only basic login supported for now

@csrf_exempt
def index(request:HttpRequest):
    if request.method != "POST":
        return HttpResponse(status=405)
    data = json.loads(request.body.decode("utf-8"))
    if data is None: return JsonResponse({"error": "Invalid or empty JSON body"}, status=400)
    authToken = data.get('token')
    
    if authToken:
        try:
            token = Token.objects.get(key=authToken)
        except Token.DoesNotExist:
            return HttpResponse(status=401)
        # Validate the token and retrieve the user
        token = Token.objects.get(key=authToken)
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