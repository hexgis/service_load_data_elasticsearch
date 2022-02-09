import logging

from datetime import datetime
from requests.models import Response
from rest_framework import generics, response, status

from elastic import models
from detection import utils


logger = logging.getLogger('django')


class UpdateDetectionView(generics.CreateAPIView):
    """Main Upload Json View.

    Does the full upload process. Removing previos data, creating new
    structure and uploading all content into ElasticSearch Server.
    """

    def __init__(self):
        self.util_class = utils.Utils()

    def post(self, request: object) -> Response:
        """Post method that does the full process.

        Includes delete, create and upload processes.

        Args:
            request (object): request sent to post url

        Returns:
            Response: Response object
        """

        try:
            es_structure, _ = models.Structure.objects.get_or_create(
                identifier='Detection'
            )

            logger.info(
                f'[{datetime.now() - self.util_class.now}]'
                f' starting process: '
            )

            json_file = self.util_class.load_detection_file(
                request.data.get('file')
            )

            detection_series = self.util_class.serialize_detection_file(
                json_file
            )

            ClearDetectionStructure().delete(request)
            CreateDetectionStructure().put(request)

            insertion_errors = self.util_class.send_bulk_list(
                detection_series, es_structure
            )

            if insertion_errors:
                response_data = {
                    'msg': 'Some data were not inserted',
                    'number_of_errors': len(insertion_errors),
                    'errors_id_list':
                        [error['id'] for error in insertion_errors],
                    'errors': insertion_errors,
                }
                logger.warning(response_data)
                return response.Response(
                    response_data, status=status.HTTP_201_CREATED
                )

            return response.Response(
                {'msg': 'Created'}, status=status.HTTP_201_CREATED
            )

        except Exception as exc:
            logger.warning(
                f'[WARNING] Exception while uploading detection: {exc}'
            )
            return response.Response(
                {'msg': str(exc)}, status=status.HTTP_404_NOT_FOUND
            )


class ClearDetectionStructure(generics.DestroyAPIView):
    """Clear detection view."""

    def __init__(self):
        self.util_class = utils.Utils()

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
        es_structure = models.Structure.objects.get(
            identifier='Detection')

        self.util_class.delete_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Clear!')

        return response.Response(
            {'msg': 'Index removed'}, status=status.HTTP_200_OK
        )


class CreateDetectionStructure(generics.UpdateAPIView):
    """Create detection Structure of ES Server view."""

    def __init__(self):
        self.util_class = utils.Utils()

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
        es_structure = models.Structure.objects.get(
            identifier='Detection')

        self.util_class.create_es_structure(es_structure)

        logger.info(f'[{datetime.now() - self.util_class.now}] Created!')

        return response.Response(
            {'msg': 'Structure created'}, status=status.HTTP_200_OK
        )
