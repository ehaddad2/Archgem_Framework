from django.http import HttpResponse, JsonResponse
from django.http import HttpRequest
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json
from Home.models import Gem
from django.contrib.auth.decorators import login_required
import django
'''
Summary: 
Request: 
Response: 
'''

@login_required()
def Search(request:HttpRequest):
    centerLat = 0
    centerLong = 0
    spanDeltaLat = float('inf')
    spanDeltaLong = float('inf')
    startsWith = ""

    try:
        req = json.loads(request.body)
        centerLat = req.get('centerLat', centerLat)
        centerLong = req.get('centerLong', centerLong)
        spanDeltaLat = req.get('spanDeltaLat', spanDeltaLat)
        spanDeltaLong = req.get('spanDeltaLong', spanDeltaLong)
        startsWith = req.get('startsWith', startsWith)

        stringMatchedGems = Gem.objects.filter(name__startswith=startsWith)
        nearby_gems_data = []

        for gem in stringMatchedGems:
            if (abs(centerLat - gem.latitude) <= spanDeltaLat) and (abs(centerLong - gem.longitude) <= spanDeltaLong):
                gem_data = {
                    'id': str(gem.uid),
                    'name': gem.name,
                    'lat': gem.latitude,
                    'long': gem.longitude,
                    'address': gem.address,
                    'city': gem.city,
                    'country': gem.country,
                    'description': gem.description,
                    'architect': gem.architect_name,
                    'constructionYear': gem.construction_year,
                    'renovationYear': gem.renovation_year,
                    'style': gem.style,
                    'imageUrl': str(gem.image_url) if gem.image_url else None,
                    'website': str(gem.website) if gem.website else None,
                    'type': gem.type
                }
                nearby_gems_data.append(gem_data)

        return JsonResponse({'gems': nearby_gems_data})

    except:
        return HttpResponse("Error retrieving gems", status=400)