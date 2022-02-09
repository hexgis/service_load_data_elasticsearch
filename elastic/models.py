from django.db import models
from django.core.serializers import json


class Structure(models.Model):
    """Model for dealing with different ElasticSearch structures.

    Stores in a sqlite database.
    """

    identifier = models.CharField(max_length=255)
    index = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    bulk_size_request = models.IntegerField(default=1000)
    structure = models.JSONField(encoder=json.DjangoJSONEncoder)

    class Meta:
        ordering = ['url', 'identifier']

    def __str__(self):
        return f'{self.identifier}'
