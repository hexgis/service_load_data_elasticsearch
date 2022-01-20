import logging
import json
import math
import requests
import pandas as pd
import urllib3
import homura
import os

from datetime import datetime
from urllib import parse
from json.decoder import JSONDecodeError
from requests.adapters import HTTPAdapter

from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from rest_framework import status

from .serializers import DetectionSerializer
from .models import Detection, BasicElasticStructure

urllib3.disable_warnings()

logger = logging.getLogger('django')


class UtilFunctions:
    """Util Class for generic code on dealing with ES data."""

    now = datetime.now()  # Timing full process.

    # Creating session for retry attempts (dns error) and retry object.
    session = requests.Session()
    retry = urllib3.Retry(connect=10, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)

    # Adding addapter to http/https requests sessions.
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    def create_es_structure(self, es_structure: BasicElasticStructure):
        """Method for sending a new mapping structure for ES Server.

        Args:
            es_structure (BasicElasticStructure): A BasicElasticStructure
                containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant insert the new structure
                into ES Server.
        """
        req = self.session.put(
            parse.urljoin(es_structure.url, es_structure.index),
            headers={"content-type": "application/json"},
            json=json.loads(es_structure.structure),
            verify=settings.VERIFY_SSL
        )

        if req.status_code != status.HTTP_200_OK and \
           req.status_code != status.HTTP_404_NOT_FOUND:
            log = (
                f'Elastic Search clearing procedure returned error. '
                f'Status code: {req.status_code} ${req.text}'
            )
            logger.warning(log)
            raise ValueError(log)

    def delete_es_structure(self, es_structure: BasicElasticStructure):
        """Method for deleting any ElasticSearch index structure.

        Args:
            es_structure (BasicElasticStructure): A BasicElasticStructure
                containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant delete previous structure loaded
            into ES Server
        """
        req = self.session.delete(
            parse.urljoin(es_structure.url, es_structure.index),
            verify=settings.VERIFY_SSL
        )

        if req.status_code != status.HTTP_200_OK and \
           req.status_code != status.HTTP_404_NOT_FOUND:
            log = (
                f'Elastic Search clearing procedure returned error.'
                f'Status code: {req.status_code} ${req.text}'
            )
            logger.warning(log)
            raise ValueError(log)

    def serialize_detection_file(self, json_file: object) -> pd.Series:
        """Method for serializing the uploaded json object.

        Serialize data into a Panda Series.

        Args:
            json_file (object): The json loaded from the json file uploaded

        Raises:
            ValueError: Raises error if there is any problem serializing data

        Returns:
           pd.Series : Returns a new Pandas Series to be dealt further
        """
        logger.info(f'[{datetime.now() - self.now}] serializing....')
        try:
            serializer = DetectionSerializer(
                data=json_file['features'], many=True)
            serializer.is_valid(raise_exception=True)

            logger.info(f'[{datetime.now() - self.now}] Serialized!')

            return self._create_detection_series(
                serializer.validated_data)
        except Exception as exc:
            log = f'Internal error: {str(exc)}'
            logger.warning(log)
            raise ValueError(log)

    def load_file(self, file_url: str) -> object:
        """Loads a uploaded json file into a json object.

        Args:
            file_url (str): url for file download

        Raises:
            ValueError: Raises error if its not possible to parse Json File

        Returns:
            object: Json Object parsed
        """
        try:
            file_content = self._download_file_from_url(file_url)
            return json.loads(file_content)
        except JSONDecodeError:
            log = f'Unexpected sent json data.'
            logger.warning(log)
            raise ValueError(log)
        except Exception:
            log = f'File not found.'
            logger.warning(log)
            raise ValueError(log)

    def _download_file_from_url(self, file_url: str) -> object:
        """Download file from a specific sent url

        Args:
            file_url (str): Url for downloading the file

        Returns:
            object: returns the read file.
        """
        try:
            file_path = settings.JSON_TEMP_FILE

            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)

            homura.download(file_url, file_path)
            json_file = open(file_path, 'r+')
            return json_file.read()
        except Exception:
            raise

    def _create_detection_series(self, data: object) -> pd.Series:
        """Creates a Panda Series with a serialized data.

        Args:
            data (object): Serialized and validated Json data

        Returns:
            pd.Series: returns a Panda Series with all Detection Models
        """
        logger.info(f'[{datetime.now() - self.now}] creating series....')

        pd_detections = pd.Series(
            [Detection(**value) for value in data])

        logger.info(f'[{datetime.now() - self.now}] series created!')
        return pd_detections

    def send_bulk_list(
        self,
        bulk_list: pd.Series,
        es_structure: BasicElasticStructure
    ) -> list:
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
        logger.info(
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

            logger.info(
                f'[{datetime.now() - self.now}] '
                f'sending chunk {chunk_id + 1} ({lower_limiter + 1}'
                f' to {higher_limiter} elements)....'
            )

            body = [t.get_es_insertion_line()
                    for t in bulk_list[lower_limiter:higher_limiter]]

            req = self.session.post(
                parse.urljoin(
                    es_structure.url, ''.join([es_structure.index, '/_bulk'])),
                headers={"content-type": "application/json"},
                data="".join(body),
                verify=settings.VERIFY_SSL
            )

            if req.status_code != 200:
                log = (
                    f'Elastic Search returned error inserting data. '
                    f'Status code: {req.status_code} ${req.text}'
                )
                logging.warning(log)
                raise ValueError(log)

            if req.json()['errors']:
                insertion_errors.extend([
                    {
                        'error': i['create']['error']['reason'],
                        'caused': i['create']['error']['caused_by']
                    } for i in req.json()['items']
                    if i['create']['status'] == 400
                ])

        logger.info(f'[{datetime.now() - self.now}] Sent')
        return insertion_errors
