from rest_framework import serializers

from .models import Detection


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = (
            'id',
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
            'geom'
        )
