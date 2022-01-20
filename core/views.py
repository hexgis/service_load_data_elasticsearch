
import logging
from datetime import datetime

from requests.models import Response
from rest_framework import generics, response, status

from .models import BasicElasticStructure
from .utils import UtilFunctions


logger = logging.getLogger('django')


class UpdateDetectionView(generics.CreateAPIView):
    """Main Upload Json View.

    Does the full upload process. Removing previos data, creating new
    structure and uploading all content into ElasticSearch Server.
    """

    def __init__(self):
        self.util_class = UtilFunctions()

    def post(self, request: object) -> Response:
        """Does the full process.

        Args:
            request (object): request sent to post url

        Returns:
            Response: Response object
        """

        try:
            es_structure, _ = BasicElasticStructure.objects.get_or_create(
                identifier='Detection')

            logger.info(
                f'[{datetime.now() - self.util_class.now}]'
                f' starting process: '
            )
            json_file = self.util_class.load_file(request.data.get('file'))

            detection_series = \
                self.util_class.serialize_detection_file(json_file)

            ClearDetectionStructure().delete(request)
            CreateDetectionStructure().put(request)

            insertion_errors = self.util_class.send_bulk_list(
                detection_series, es_structure)

            if insertion_errors:
                response_data = {
                    'msg': 'Some data were not inserted',
                    'errors': insertion_errors
                }
                logger.warning(response_data)
                return response.Response(
                    response_data, status=status.HTTP_400_BAD_REQUEST)

            response_data = {'msg': "Created"}
            return response.Response(
                response_data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.warning(
                f'[WARNING] Exception while uploading detection: {exc}')
            return response.Response(
                {"msg": str(exc)}, status=status.HTTP_404_NOT_FOUND
            )


class ClearDetectionStructure(generics.DestroyAPIView):
    """Clear detection view."""

    def __init__(self):
        self.util_class = UtilFunctions()

    def delete(self, request: object) -> Response:
        """Delete method for dealing with clear ES Structure.

        Args:
            request (object): Request sent for delete url

        Returns:
            Response: Response object
        """
        logger.info(
            f'[{datetime.now() - self.util_class.now}]'
            f' Clearing structure...'
        )
        es_structure = BasicElasticStructure.objects.get(
            identifier='Detection')

        self.util_class.delete_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Clear!')

        return response.Response(
            {"msg": "Index removed"}, status=status.HTTP_200_OK
        )


class CreateDetectionStructure(generics.UpdateAPIView):
    """Clear detection Structure from ES Server view."""

    def __init__(self):
        self.util_class = UtilFunctions()

    def put(self, request: object) -> Response:
        """Put method for dealing with inserting a new ES Structure.

        Args:
            request (object): Request sent for put url

        Returns:
            Response: Response Object
        """
        logger.info(
            f'[{datetime.now() - self.util_class.now}]'
            f' Creating structure...'
        )
        es_structure = BasicElasticStructure.objects.get(
            identifier='Detection')

        self.util_class.create_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Created!')

        return response.Response(
            {"msg": "Structure created"}, status=status.HTTP_200_OK
        )
