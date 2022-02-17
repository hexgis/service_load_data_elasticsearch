from django.db import models
from django.core.serializers import json
from django.utils.translation import ugettext_lazy as _


class Structure(models.Model):
    """Model for dealing with different ElasticSearch structures.

    Stores in a sqlite database.
    """

    identifier = models.CharField(
        _('Identifier'),
        max_length=255
    )

    index = models.CharField(
        _('Index'),
        max_length=255
    )

    url = models.CharField(
        _('Structure url'),
        max_length=255
    )

    bulk_size_request = models.IntegerField(
        _('Bulk size per request'),
        default=1000
    )

    structure = models.JSONField(
        _('Json Structure'),
        encoder=json.DjangoJSONEncoder
    )

    class Meta:
        ordering = ('url', 'identifier', )

    def __str__(self):
        return f'{self.identifier}'
