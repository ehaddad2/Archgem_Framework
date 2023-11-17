from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
from Home.models import Gem
from math import cos, asin, sqrt
import math
from django.contrib.auth.decorators import login_required

''' 
Summary: Gets gems around user based on their current location
Request: requires the (lat,long) of user current loc AND search radius
Response: returns a list of gem dicts within the loc search radius
'''

@login_required()
def index(request):
    user_lat = float(request.GET.get('lat'))
    user_long = float(request.GET.get('long'))
    radius = float(request.GET.get('radius'))

    nearby_gems = []
    for gem in Gem.objects.all():
        dist = distance(user_lat, user_long, gem.latitude, gem.longitude)
        if dist < radius:
            nearby_gems.append({'gem':gem})

    return JsonResponse({'gems': nearby_gems})

''' 
Summary: Queries Gem database for any gems starting with specified string from request
Request: a string with which to query gem names
Response: returns a list of gems matching the query params
'''
def Search(request):
    query_string = request.GET.get('query', '')
    matching_gems = Gem.objects.filter(name__startswith=query_string)

    # Convert the gem objects to a list of dictionaries
    gems_data = [{'gem':gem} for gem in matching_gems]

    return JsonResponse({'gems': gems_data})

'''
Helper Functions
'''
#haversine
def distance(lat1, lon1, lat2, lon2):
    p =  math.pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))