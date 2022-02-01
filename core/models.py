import json as Json

from django.contrib.gis.db import models
from django.core.serializers import json


class Detection(models.Model):
    """Abstract object to deal with json file uploaded to service."""

    _id = models.IntegerField()

    tb_ciclo_monitoramento_id = models.IntegerField()

    sg_uf = models.CharField(max_length=2)

    no_estagio = models.CharField(max_length=255)

    no_imagem = models.CharField(max_length=255)

    dt_imagem = models.DateField()

    nu_orbita = models.CharField(max_length=3)

    nu_ponto = models.CharField(max_length=3)

    dt_t_zero = models.DateField()

    dt_t_um = models.DateField()

    nu_area_km2 = models.FloatField()

    nu_area_ha = models.FloatField()

    dt_cadastro = models.DateTimeField()

    latitude = models.FloatField()

    longitude = models.FloatField()

    geometry = models.GeometryField()

    class Meta:
        managed = False

    def __str__(self):
        return self.no_estagio

    def get_es_insertion_line(self):
        """Method for bulk line create string.

        Generates the whole bulk line insertion into ElasticSearch server
        for each feature inside json file.

        Returns:
            str: create line and data line separated with a new
                line character
        """

        self.id = self._id

        fields = [
            self._format_data(
                f.get_attname(),
                getattr(self, f.get_attname())
            ) for f in self._meta.get_fields() if f.get_attname() != '_id']

        es_data_header = f'{{ "create": {{ "_id": "{self._id}"}}}}'
        es_data_line = ", ".join(fields)

        return f'{es_data_header}\n{{{es_data_line}}}\n'

    def _format_data(self, field: str, value: object):
        """Method for validating each field with each type validation.

        Args:
            field (str): field name for validation
            value (object): value of the field to be validated

        Returns:
            str: returns field name and field value separated with a
            colon character
        """
        if field == 'dt_cadastro':
            value = f'"{value.replace(tzinfo=None)}"'
        elif field == 'geometry':
            value = value.geojson
        else:
            value = f'"{value}"'

        return f'"{field}": {value}'


class BasicElasticStructure(models.Model):
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
