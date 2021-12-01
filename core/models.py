from django.db import models


class Detection(models.Model):

    id = models.IntegerField(primary_key=True)

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

    geometry = models.CharField(max_length=1000)

    def __str__(self):
        return self.id + ' ' + self.dt_cadastro

    class Meta:
        managed = False
