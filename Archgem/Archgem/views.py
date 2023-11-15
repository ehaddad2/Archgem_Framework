from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token
import json

#perform series of initialization tasks
def init(request:HttpRequest):
    #generate csrf token
    if request.method == "GET":
        token = get_token(request)
        sessionID = 1 #TODO: CHANGE!
        
        response = json.dumps( {
            "SID": sessionID,
            "CSRF":token
        })
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse("Error: GET request required", status=405)