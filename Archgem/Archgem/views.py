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


def health(request: HttpRequest):
    """
    Health check endpoint. Returns 200 if DB and Cache are reachable.
    Returns 503 with error details if either fails.
    """
    from django.db import connection
    from django.core.cache import cache

    errors = []

    # Check Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        errors.append(f"Database: {str(e)}")

    # Check Redis/Cache
    try:
        cache.set("health_check", "ok", timeout=5)
        if cache.get("health_check") != "ok":
            errors.append("Cache: Failed to read/write")
    except Exception as e:
        errors.append(f"Cache: {str(e)}")

    if errors:
        return JsonResponse({"status": "unhealthy", "errors": errors}, status=503)

    return JsonResponse({"status": "healthy"}, status=200)