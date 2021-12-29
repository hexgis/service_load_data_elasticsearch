from core.models import BasicElasticStructure
from model_mommy.recipe import Recipe


class Recipes:
    """Mommy recipes used on test cases."""

    def __init__(self):
        self.es_object = Recipe(
            BasicElasticStructure,
            index='detection-test',
            identifier='Detection',
            url='http://es.xskylab.com:9200',
            bulk_size_request=1000,
            structure='{ "aliases":{}, "mappings":{' +
            '"properties":{ "id":{ "type":"keyword" }, ' +
            '"tb_ciclo_monitoramento_id":{ "type":"keyword" }, ' +
            '"sg_uf":{ "type":"keyword" }, ' +
            '"no_estagio":{ "type":"keyword" }, ' +
            '"no_imagem":{ "type":"text", "fields": ' +
            '{ "exact":{ "type":"keyword" } } }, ' +
            '"dt_imagem":{ "type":"date" }, "nu_orbita":{ ' +
            '"type":"text" }, "nu_ponto":{ "type":"text" }, ' +
            '"dt_t_zero":{ "type":"date" }, "dt_t_um":{ "type":"date" }, ' +
            '"nu_area_km2":{ "type":"double" }, "nu_area_ha":{' +
            '"type":"double" }, "dt_cadastro":{ "type":"date", ' +
            '"format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis" }, ' +
            '"geometry":{ "type":"geo_shape" } } }, ' +
            '"settings":{ "analysis":{ "filter":{ "brazilian_stemmer":{ ' +
            '"type":"stemmer", "language":"brazilian"},"brazilian_stop":{' +
            '"type":"stop", "stopwords":"_brazilian_" } }, "analyzer":{ ' +
            '"image_analyzer":{ "tokenizer":"undescore_tokenizer" } }, ' +
            '"tokenizer":{ "undescore_tokenizer":{' +
            '"type":"simple_pattern_split", "pattern":"_"}}}}}'
        )
