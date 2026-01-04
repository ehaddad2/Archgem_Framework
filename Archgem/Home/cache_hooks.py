import math
from django.core.cache import cache
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from Home.models import Gem

Z_LEVELS = (8, 9, 10, 11, 12)

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

def _cache_version():
    v = cache.get("gems_cache_version")
    if v is None:
        v = 1
        cache.set("gems_cache_version", v, None)
    return v

def _tile_key(z, x, y, version):
    return f"tile:{z}:{x}:{y}:v:{version}"

def invalidate_point(lat, lon):
    version = _cache_version()
    for z in Z_LEVELS:
        x, y = latlon_to_tile_xy(float(lat), float(lon), z)
        cache.delete(_tile_key(z, x, y, version))

@receiver(pre_save, sender=Gem)
def gem_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    old = Gem.objects.filter(pk=instance.pk).values("latitude", "longitude").first()
    if old:
        instance._old_lat = float(old["latitude"])
        instance._old_lon = float(old["longitude"])

@receiver(post_save, sender=Gem)
def gem_post_save(sender, instance, created, **kwargs):
    if created:
        invalidate_point(instance.latitude, instance.longitude)
        return
    old_lat = getattr(instance, "_old_lat", None)
    old_lon = getattr(instance, "_old_lon", None)
    if old_lat is None or old_lon is None:
        return
    new_lat = float(instance.latitude)
    new_lon = float(instance.longitude)
    if old_lat != new_lat or old_lon != new_lon:
        invalidate_point(old_lat, old_lon)
        invalidate_point(new_lat, new_lon)

@receiver(post_delete, sender=Gem)
def gem_post_delete(sender, instance, **kwargs):
    invalidate_point(instance.latitude, instance.longitude)
