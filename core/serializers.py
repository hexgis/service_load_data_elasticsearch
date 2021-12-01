from rest_framework_gis import serializers as gis_serializers
from rest_framework import serializers
from rest_framework.parsers import JSONParser, MultiPartParser

from .models import Detection


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

    def unformat_geojson(self, feature):

        # import pdb
        # pdb.set_trace()

        return {
            self.Meta.geo_field: feature["geometry"],
            'tb_ciclo_monitoramento_id': feature['properties']['tb_ciclo_monitoramento_id'],
            "no_estagio": feature["properties"]["no_estagio"],
            "no_imagem": feature["properties"]["no_imagem"],
            "dt_imagem": feature["properties"]["dt_imagem"].replace('/', '-'),
            "sg_uf": feature["properties"]["sg_uf"],
            "nu_orbita": feature["properties"]["nu_orbita"],
            "nu_ponto": feature["properties"]["nu_ponto"],
            "dt_t_zero": feature["properties"]["dt_t_zero"].replace('/', '-'),
            "dt_t_um": feature["properties"]["dt_t_um"].replace('/', '-'),
            "nu_area_km2": feature["properties"]["nu_area_km2"],
            "nu_area_ha": feature["properties"]["nu_area_ha"],
            "dt_cadastro": feature["properties"]["dt_cadastro"].replace('/', '-'),
        }

    # def to_internal_value(self, data):
    #     # for feature in data['features']:

    #     # import pdb
    #     # pdb.set_trace()

    #     return self.get_properties()

    # def create_es(self):

    #     detections = Detection(**self.data)

    #     #     print(validated_data)

    #     import pdb
    #     pdb.set_trace()

    #     return
