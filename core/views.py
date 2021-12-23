import pandas as pd
import json
import requests
import math

from io import FileIO
from json.decoder import JSONDecodeError
from django.core.files.uploadedfile import UploadedFile
from django.core.serializers import serialize
from rest_framework import generics, response, status
from requests.models import Response
from urllib import parse

from .serializers import DetectionSerializer
from .models import Detection, BasicElasticStructure
from datetime import datetime


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
            es_structure = BasicElasticStructure.objects.get(
                identifier='Detection')
            print(f'[{datetime.now() - self.util_class.now}] starting process: ')

            json_file = self.util_class.load_file(request.FILES['file'])
            detection_series = self.util_class.serialize_detection_file(
                json_file
            )

            ClearDetectionStructure.delete(request)

            CreateDetectionStructure.put(request)

            insertion_errors = self.util_class.send_bulk_list(
                detection_series, es_structure)

            if (insertion_errors):
                return response.Response({
                    'msg': 'Some data were not inserted',
                    'errors': insertion_errors
                }, status=status.HTTP_400_BAD_REQUEST)

            return response.Response(
                {'msg': "Created"}, status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            return response.Response({"msg": str(exc)}, status=404)


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
        print(f'[{datetime.now() - self.util_class.now}] Clearing structure...')
        es_structure = BasicElasticStructure.objects.get(
            identifier='Detection')

        self.util_class.delete_es_structure(es_structure)

        print(f'[{datetime.now() - self.util_class.now}] Clear!')

        return response.Response("Index removed", status=status.HTTP_200_OK)


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
        print(f'[{datetime.now() - self.util_class.now}] Creating structure...')
        es_structure = BasicElasticStructure.objects.get(
            identifier='Detection')

        self.util_class.create_es_structure(es_structure)

        print(f'[{datetime.now() - self.util_class.now}] Created!')

        return response.Response("Structure created", status=status.HTTP_200_OK)


class UtilFunctions:
    """Util Class for generic code on dealing with ES data."""

    """Variable for timing full process."""
    now = datetime.now()

    def create_es_structure(self, es_structure: BasicElasticStructure):
        """Method for sending a new mapping structure for ES Server.

        Args:
            es_structure (BasicElasticStructure): A BasicElasticStructure
            containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant insert the new structure
                into ES Server.
        """
        req = requests.put(
            parse.urljoin(es_structure.url, es_structure.index),
            headers={"content-type": "application/json"},
            json=json.loads(es_structure.structure)
        )

        if req.status_code != status.HTTP_200_OK and req.status_code != status.HTTP_404_NOT_FOUND:
            raise ValueError(
                f'Elastic Search clearing procedure returned error. \
                    Status code: {req.status_code} ${req.text}')

    def delete_es_structure(self, es_structure: BasicElasticStructure):
        """Method for deleting any ElasticSearch index structure.

        Args:
            es_structure (BasicElasticStructure): A BasicElasticStructure
                containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant delete previous structure loaded
            into ES Server
        """
        req = requests.delete(
            parse.urljoin(es_structure.url, es_structure.index),
        )

        if req.status_code != status.HTTP_200_OK and req.status_code != status.HTTP_404_NOT_FOUND:

            raise ValueError(f'Elastic Search clearing procedure \
                    returned error. Status code: {req.status_code} ${req.text}')

    def serialize_detection_file(self, json_file: object) -> pd.Series:
        """Method for serializing the uploaded json object into a Panda Series.

        Args:
            json_file (object): The json loaded from the json file uploaded

        Raises:
            ValueError: Raises error if there is any problem serializing the data

        Returns:
           pd.Series : Returns a new Pandas Series to be dealt further
        """
        print(f'[{datetime.now() - self.now}] serializing....')
        try:
            serializer = DetectionSerializer(
                data=json_file['features'], many=True)
            serializer.is_valid(raise_exception=True)

            print(f'[{datetime.now() - self.now}] Serialized!')

            return self._create_detection_series(
                serializer.validated_data)
        except Exception as exc:
            raise ValueError(f'Internal error: {str(exc)}')

    def load_file(self, file: UploadedFile) -> object:
        """Loads a uploaded json file into a json object.

        Args:
            file (UploadedFile): Uploaded Json File

        Raises:
            ValueError: Raises error if its not possible to parse Json File

        Returns:
            object: Json Object parsed
        """
        try:
            file_content = file.read()
            return json.loads(file_content)
        except JSONDecodeError as json_error:
            raise ValueError(f'Unexpected sent json data')

    def _create_detection_series(self, data: object) -> pd.Series:
        """Creates a Panda Series with a serialized data.

        Args:
            data (object): Serialized and validated Json data

        Returns:
            pd.Series: returns a Panda Series with all Detection Models
        """
        print(f'[{datetime.now() - self.now}] creating series....')

        pd_detections = pd.Series(
            [Detection(**value) for value in data])

        print(f'[{datetime.now() - self.now}] series created!')
        return pd_detections

    def send_bulk_list(
            self,
            bulk_list: pd.Series,
            es_structure: BasicElasticStructure) -> list:
        """Method for sending all Detections to a ElasticSearch Bulk request.

        Args:
            bulk_list (pd.Series): a Panda Series with all Detections
            es_structure (BasicElasticStructure): a basic ElasticSearch
                structure with all needed data.

        Raises:
            ValueError: Raises error if there is any inserting error.

        Returns:
            list : A list containing all insertion errors.
        """
        print(
            f'[{datetime.now() - self.now}] '
            f'preparing bulk list of size {bulk_list.size}....'
        )

        bulk_size = int(es_structure.bulk_size_request) or 1
        insertion_errors = []
        chunks = math.ceil(bulk_list.size / bulk_size)

        for chunk_id in list(range(chunks)):
            lower_limiter = (chunk_id) * bulk_size
            higher_limiter = (chunk_id + 1) * bulk_size

            if higher_limiter >= len(bulk_list):
                higher_limiter = len(bulk_list)

            print(
                f'[{datetime.now() - self.now}] '
                f'sending chunk {chunk_id + 1} ({lower_limiter + 1}'
                f' to {higher_limiter} elements)....'
            )

            body = [t.get_es_insertion_line()
                    for t in bulk_list[lower_limiter:higher_limiter]]

            req = requests.post(
                parse.urljoin(es_structure.url, [es_structure.index, '_bulk']),
                headers={"content-type": "application/json"},
                data="".join(body)
            )

            if req.status_code != 200:
                raise ValueError(
                    f'Elastic Search returned error inserting data. '
                    f'Status code: {req.status_code} ${req.text}'
                )

            if req.json()['errors']:
                insertion_errors.extend([
                    {
                        'error': i['create']['error']['reason'],
                        'caused': i['create']['error']['caused_by']
                    } for i in req.json()['items']
                    if i['create']['status'] == 400
                ])

        print(f'[{datetime.now() - self.now}] Sent')

        return insertion_errors
