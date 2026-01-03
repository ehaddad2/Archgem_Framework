from django.db import models
from django.urls import reverse
import uuid

#Models for the Navigation View
class Gem(models.Model):

    # Fields
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    architect_name = models.CharField(max_length=100, blank=True, null=True)
    construction_year = models.IntegerField(blank=True, null=True)# if None, then its still in progress
    renovation_year = models.IntegerField(blank=True, null=True)# if None, then never renovated
    style = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)


    def _bump_cache_version(self):
        try:
            cache.incr("gems_cache_version")
        except ValueError:
            cache.set("gems_cache_version", 2, None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._bump_cache_version()

    def delete(self, *args, **kwargs):
        out = super().delete(*args, **kwargs)
        self._bump_cache_version()
        return out

    # Metadata
    class Meta:
        db_table = 'gem_locations'
        unique_together = ['latitude', 'longitude']

    # Methods
    def get_absolute_url(self):
        return reverse('gem-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.name