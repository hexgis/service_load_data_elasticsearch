import logging
from datetime import datetime

from requests.models import Response
from rest_framework import generics, response, status

from elastic.models import Structure as ElasticStructure
from elastic.utils import UtilFunctions


logger = logging.getLogger('django')


class UpdateSoyView(generics.CreateAPIView):
    def __init__(self):
        self.util_class = UtilFunctions()

    def post(self, request: object) -> Response:
        try:
            es_structure, _ = ElasticStructure.objects.get_or_create(
                identifier='Soy'
            )

            logger.info(
                f'[{datetime.now() - self.util_class.now}]' 
                f' starting process: '
            )
            text_file = self.util_class.load_soy_file(request.data.get('file'))

            soy_series = self.util_class.serialize_soy_file(text_file)

            ClearSoyStructiore().delete(request)
            CreateSoyStructure().put(request)

            insertion_errors = self.util_class.send_bulk_list(
                soy_series, es_structure
            )

        except Exception as exc:
            return response.Response(
                {'msg': str(exc)}, status=status.HTTP_404_NOT_FOUND
            )

        return response.Response({'msg': 'Created'}, status=status.HTTP_201_CREATED)


class ClearSoyStructiore(generics.DestroyAPIView):
    def __init__(self):
        self.util_class = UtilFunctions()

    def delete(self, request: object) -> Response:
        logger.info(
            f'[{datetime.now() - self.util_class.now}]' 
            f' Clearing structure...'
        )
        es_structure = ElasticStructure.objects.get(identifier='Soy')

        self.util_class.delete_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Clear!')

        return response.Response({'msg': 'Index removed'}, status=status.HTTP_200_OK)


class CreateSoyStructure(generics.UpdateAPIView):
    def __init__(self):
        self.util_class = UtilFunctions()

    def put(self, request: object) -> Response:
        logger.info(
            f'[{datetime.now() - self.util_class.now}]' f' Creating structure...'
        )
        es_structure = ElasticStructure.objects.get(identifier='Soy')

        self.util_class.create_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Created!')

        return response.Response(
            {'msg': 'Structure created'}, status=status.HTTP_200_OK
        )
