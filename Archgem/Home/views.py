import json
import math
import traceback
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from Home.models import Gem

Z_LEVELS = (8, 9, 10, 11, 12)

# Cache the version in-memory for 60 seconds to reduce Redis reads
_version_cache = {"value": None, "expires": 0}

def _get_cache_version():
    import time
    now = time.time()
    if _version_cache["value"] is not None and now < _version_cache["expires"]:
        return _version_cache["value"]
    
    v = cache.get("gems_cache_version")
    if v is None:
        v = 1
        cache.set("gems_cache_version", v, None)
    
    _version_cache["value"] = v
    _version_cache["expires"] = now + 60  # Cache locally for 60 seconds
    return v

def _tile_key(z, x, y, version):
    return f"tile:{z}:{x}:{y}:v:{version}"

def invalidate_tiles_for_point(lat, lon):
    version = _get_cache_version()
    for z in Z_LEVELS:
        x, y = latlon_to_tile_xy(lat, lon, z)
        cache.delete(_tile_key(z, x, y, version))

def invalidate_tiles_for_move(old_lat, old_lon, new_lat, new_lon):
    invalidate_tiles_for_point(old_lat, old_lon)
    invalidate_tiles_for_point(new_lat, new_lon)
    
def z_bucket_from_span(span_lat):
    if span_lat >= 8:
        return 8
    if span_lat >= 3:
        return 9
    if span_lat >= 1.2:
        return 10
    if span_lat >= 0.5:
        return 11
    return 12

def latlon_to_tile_xy(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)

    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

    if x < 0:
        x = 0
    if x >= n:
        x = n - 1
    if y < 0:
        y = 0
    if y >= n:
        y = n - 1

    return x, y

def tile_bbox(z, x, y):
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0

    def y_to_lat(y_idx, z_):
        n_ = 2 ** z_
        merc = math.pi * (1.0 - 2.0 * y_idx / n_)
        return math.degrees(math.atan(math.sinh(merc)))

    lat_max = y_to_lat(y, z)
    lat_min = y_to_lat(y + 1, z)

    return lat_min, lat_max, lon_min, lon_max

def tiles_for_viewport(center_lat, center_lon, span_lat, span_lon, z):
    lat_min = center_lat - span_lat
    lat_max = center_lat + span_lat
    lon_min = center_lon - span_lon
    lon_max = center_lon + span_lon

    x0, y0 = latlon_to_tile_xy(lat_max, lon_min, z)
    x1, y1 = latlon_to_tile_xy(lat_min, lon_max, z)

    x_min = min(x0, x1)
    x_max = max(x0, x1)
    y_min = min(y0, y1)
    y_max = max(y0, y1)

    out = []
    x = x_min
    while x <= x_max:
        y = y_min
        while y <= y_max:
            out.append((z, x, y))
            y += 1
        x += 1

    return out, lat_min, lat_max, lon_min, lon_max

@login_required()
def Search(request):
    try:
        req = json.loads(request.body)

        center_lat = float(req.get("centerLat", 0.0))
        center_lon = float(req.get("centerLong", 0.0))
        span_lat = float(req.get("spanDeltaLat", 1.0))
        span_lon = float(req.get("spanDeltaLong", 1.0))
        starts_with = req.get("startsWith", "")

        z = z_bucket_from_span(span_lat)
        tiles, lat_min, lat_max, lon_min, lon_max = tiles_for_viewport(center_lat, center_lon, span_lat, span_lon, z)

        # Use in-memory cached version to avoid Redis read
        version = _get_cache_version()

        # OPTIMIZATION: Batch fetch all tile keys in a single Redis call
        cache_keys = [f"tile:{zt}:{xt}:{yt}:v:{version}" for zt, xt, yt in tiles]
        cached_values = cache.get_many(cache_keys)  # Single Redis MGET call
        
        id_set = set()
        tiles_to_fill = []  # Collect tiles that need DB queries
        
        # Process cached results
        for i, (zt, xt, yt) in enumerate(tiles):
            cache_key = cache_keys[i]
            payload = cached_values.get(cache_key)
            
            if payload is None:
                # Cache miss - need to query DB
                tiles_to_fill.append((zt, xt, yt, cache_key))
            else:
                # Cache hit
                for uid in payload:
                    id_set.add(uid)

        # OPTIMIZATION: Batch set cache for all misses
        if tiles_to_fill:
            cache_to_set = {}
            for zt, xt, yt, cache_key in tiles_to_fill:
                t_lat_min, t_lat_max, t_lon_min, t_lon_max = tile_bbox(zt, xt, yt)

                qs = Gem.objects.filter(
                    latitude__gte=t_lat_min,
                    latitude__lte=t_lat_max,
                    longitude__gte=t_lon_min,
                    longitude__lte=t_lon_max,
                )

                payload = [str(uid) for uid in qs.values_list("uid", flat=True)]
                cache_to_set[cache_key] = payload
                
                for uid in payload:
                    id_set.add(uid)
            
            # Single Redis MSET call for all new tiles
            cache.set_many(cache_to_set, timeout=1800)

        if len(id_set) == 0:
            return JsonResponse({"gems": []})

        gems = Gem.objects.filter(
            uid__in=list(id_set),
            latitude__gte=lat_min,
            latitude__lte=lat_max,
            longitude__gte=lon_min,
            longitude__lte=lon_max,
        )

        if starts_with:
            gems = gems.filter(name__startswith=starts_with) 
            
        out = []
        for g in gems:
            out.append({
                "id": str(g.uid),
                "name": g.name,
                "lat": g.latitude,
                "long": g.longitude,
                "address": g.address,
                "city": g.city,
                "country": g.country,
                "description": g.description,
                "architect": g.architect_name,
                "constructionYear": g.construction_year,
                "renovationYear": g.renovation_year,
                "style": g.style,
                "imageUrl": str(g.image_url) if g.image_url else None,
                "website": str(g.website) if g.website else None,
                "type": g.type,
            })

        return JsonResponse({"gems": out})

    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse(f"Error retrieving gems: {repr(e)}", status=400)
