from django.contrib.gis.db import models
from django.conf import settings
from django.core.serializers import json


class Detection(models.Model):
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

    geometry = models.GeometryField(srid=4674)

    def __str__(self):
        return self.no_estagio

    def get_es_insertion_line(self):

        fields = [f'"{f.get_attname()}": "{getattr(self, f.get_attname())}"' for f in self._meta.get_fields(
        ) if f.get_attname() != 'id']

        # import pdb
        # pdb.set_trace()

        es_data_header = f'{{ "create": {{ "_id": "{self._id}"}}}}'
        es_data_line = ", ".join(fields)

        return f'{es_data_header}\n{{{es_data_line}}}'

    class Meta:
        managed = False


class BasicElasticStructure(models.Model):
    identifier = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    bulk_size_request = models.IntegerField(default=1000)
    structure = models.JSONField(encoder=json.DjangoJSONEncoder)
