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
    architect_name = models.CharField(max_length=100)

    # Metadata
    class Meta:
        db_table = 'gem_locations'
        unique_together = ['latitude', 'longitude']

    # Methods
    def get_absolute_url(self):
        return reverse('gem-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.name