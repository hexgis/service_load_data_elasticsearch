from django.contrib.gis import geos
from rest_framework_gis import serializers as gis_serializers
from rest_framework import serializers
from rest_framework.parsers import JSONParser, MultiPartParser

from .models import Detection
import json


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    parser_classes = (MultiPartParser)

    def create(self, validated_data):
        # import pdb
        # pdb.set_trace()
        return validated_data


class DetectionSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Detection
        geo_field = 'geometry'
        fields = (
            '_id',
            'tb_ciclo_monitoramento_id',
            'no_estagio',
            'no_imagem',
            'dt_imagem',
            'sg_uf',
            'nu_orbita',
            'nu_ponto',
            'dt_t_zero',
            'dt_t_um',
            'nu_area_km2',
            'nu_area_ha',
            'dt_cadastro',
        )

    # def to_internal_data(self, feature):

    #     return {
    #         'geometry': geos.GEOSGeometry(geos.GEOSGeometry(json.dumps(feature["geometry"])).wkt, srid=4674),
    #         'tb_ciclo_monitoramento_id': feature['properties']['tb_ciclo_monitoramento_id'],
    #         "no_estagio": feature["properties"]["no_estagio"],
    #         "no_imagem": feature["properties"]["no_imagem"],
    #         "dt_imagem": feature["properties"]["dt_imagem"].replace('/', '-'),
    #         "sg_uf": feature["properties"]["sg_uf"],
    #         "nu_orbita": feature["properties"]["nu_orbita"],
    #         "nu_ponto": feature["properties"]["nu_ponto"],
    #         "dt_t_zero": feature["properties"]["dt_t_zero"].replace('/', '-'),
    #         "dt_t_um": feature["properties"]["dt_t_um"].replace('/', '-'),
    #         "nu_area_km2": feature["properties"]["nu_area_km2"],
    #         "nu_area_ha": feature["properties"]["nu_area_ha"],
    #         "dt_cadastro": feature["properties"]["dt_cadastro"].replace('/', '-'),
    #     }

        # detection = Detection.objects.create(
        #     geometry=geos.GEOSGeometry(geos.GEOSGeometry(
        #         json.dumps(data["geometry"])).wkt, srid=4674),
        #     tb_ciclo_monitoramento_id=data['properties']['tb_ciclo_monitoramento_id'],
        #     no_estagio=data["properties"]["no_estagio"],
        #     no_imagem=data["properties"]["no_imagem"],
        #     dt_imagem=data["properties"]["dt_imagem"].replace(
        #         '/', '-'),
        #     sg_uf=data["properties"]["sg_uf"],
        #     nu_orbita=data["properties"]["nu_orbita"],
        #     nu_ponto=data["properties"]["nu_ponto"],
        #     dt_t_zero=data["properties"]["dt_t_zero"].replace(
        #         '/', '-'),
        #     dt_t_um=data["properties"]["dt_t_um"].replace('/', '-'),
        #     nu_area_km2=data["properties"]["nu_area_km2"],
        #     nu_area_ha=data["properties"]["nu_area_ha"],
        #     dt_cadastro=data["properties"]["dt_cadastro"].replace(
        #         '/', '-')
        # )

        # # import pdb
        # # pdb.set_trace()

        # return detection

    # def create(self, validated_data):
    #     return Detection(**validated_data)

    def unformat_geojson(self, feature):
        # import pdb
        # pdb.set_trace()

        attr = {
            '_id': feature['properties']['id'],
            'geometry': geos.GEOSGeometry(geos.GEOSGeometry(json.dumps(feature["geometry"])).wkt, srid=4674),
            'tb_ciclo_monitoramento_id': feature['properties']['tb_ciclo_monitoramento_id'],
            "no_estagio": feature["properties"]["no_estagio"],
            "no_imagem": feature["properties"]["no_imagem"],
            "sg_uf": feature["properties"]["sg_uf"],
            "nu_orbita": feature["properties"]["nu_orbita"],
            "nu_ponto": feature["properties"]["nu_ponto"],
            "nu_area_km2": feature["properties"]["nu_area_km2"],
            "nu_area_ha": feature["properties"]["nu_area_ha"],
            "dt_t_zero": feature["properties"]["dt_t_zero"].replace('/', '-'),
            "dt_t_um": feature["properties"]["dt_t_um"].replace('/', '-'),
            "dt_imagem": feature["properties"]["dt_imagem"].replace('/', '-'),
            "dt_cadastro": feature["properties"]["dt_cadastro"].replace('/', '-'),
        }

        return attr

    # def create(self, validated_data):
    #     return validated_data

    # def to_internal_value(self, data):
    #     return data

    # def create_es(self):
    #     detections = Detection(**self.data)

    #     #     print(validated_data)

    #     import pdb
    #     pdb.set_trace()

    #     return
