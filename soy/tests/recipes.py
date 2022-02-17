from elastic.models import Structure
from model_mommy.recipe import Recipe


class Recipes:
    """Mommy recipes used on test cases."""

    def __init__(self):
        self.es_object = Recipe(
            Structure,
            index="soy-test",
            identifier="Soy",
            url="https://es.xskylab.com:9200",
            bulk_size_request=1000,
            structure='{"aliases":{},"mappings":{'
            + '"properties":{"ano":{"type":"double"},"area_plantada"'
            + ':{"type":"double"},"area_produtividade":{"type":"double"},'
            + '"id":{"type":"keyword"},"uf":{"type":"keyword","fields":'
            + '{"keyword": {"type": "keyword"}}}}}, "settings": {"analysis"'
            + ': {"filter": {"brazilian_stemmer": {"type": "stemmer", '
            + '"language": "brazilian"}, "brazilian_stop": {"type": "stop"'
            + ', "stopwords": "_brazilian_"}}, "analyzer": {"image_analyzer":'
            + ' {"tokenizer": "undescore_tokenizer"}}, "tokenizer": '
            + '{"undescore_tokenizer": {"type": "simple_pattern_split", '
            + '"pattern": "_"}}}}}',
        )
