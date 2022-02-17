import logging
import json
import math
import requests
import urllib3
import homura
import tempfile
import pandas as pd

from datetime import datetime
from urllib import parse
from requests.adapters import HTTPAdapter

from django.conf import settings
from rest_framework import status

from elastic import models as elastic_models

urllib3.disable_warnings()

logger = logging.getLogger('django')


class Utils:
    """Util Class for Detection data on Elastic Search."""

    now = datetime.now()  # Timing full process.

    # Creating session for retry attempts (dns error) and retry object.
    session = requests.Session()
    retry = urllib3.Retry(connect=10, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)

    # Adding addapter to http/https requests sessions.
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    def __get_bulk_string(self) -> str:
        """Internal function to return, for each index, its bulk line.

        It needs an definition for each index app created on the service.

        Returns:
            str: the bulk line into single line string
        """
        raise ValueError('Method __get_bulk_string not implemented.')

    def _download_file_from_url(self, file_url: str, extension: str) -> object:
        """Download file from a specific sent url.

        Args:
            file_url (str): Url for downloading the file
            extension (str): Type of extension for the file

        Returns:
            object: returns the read file.
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=extension)

            if (not file_url):
                raise ValueError('No url file were sent')

            homura.download(file_url, temp_file.name)
            json_file = open(temp_file.name, 'r+')
            return json_file
        except Exception:
            raise

    def create_es_structure(self, es_structure: elastic_models.Structure):
        """Method for sending a new mapping structure for ES Server.

        Args:
            es_structure (elastic_models.Structure): A Elastic structure
                containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant insert the new structure
                into ES Server.
        """
        req = self.session.put(
            parse.urljoin(es_structure.url, es_structure.index),
            headers={'content-type': 'application/json'},
            json=json.loads(es_structure.structure),
            verify=settings.VERIFY_SSL,
        )

        if req.status_code != status.HTTP_200_OK and \
           req.status_code != status.HTTP_404_NOT_FOUND:
            log = (
                f'Elastic Search clearing procedure returned error.\n'
                f'Status code: {req.status_code} ${req.text}'
            )
            logger.warning(log)
            raise ValueError(log)

    def delete_es_structure(self, es_structure: elastic_models.Structure):
        """Method for deleting any ElasticSearch index structure.

        Args:
            es_structure (elastic_models.Structure): A Elastic structure
                containing all needed ES Data.

        Raises:
            ValueError: Raises error if cant delete previous structure loaded
            into ES Server
        """
        req = self.session.delete(
            parse.urljoin(es_structure.url, es_structure.index),
            verify=settings.VERIFY_SSL,
        )

        if req.status_code != status.HTTP_200_OK and \
           req.status_code != status.HTTP_404_NOT_FOUND:
            log = (
                f'Elastic Search clearing procedure returned error.\n'
                f'Status code: {req.status_code} ${req.text}'
            )
            logger.warning(log)
            raise ValueError(log)

    def send_bulk_list(
        self,
        bulk_list: pd.Series,
        es_structure: elastic_models.Structure
    ) -> list:
        """Method for sending all Detections to a ElasticSearch Bulk request.

        Args:
            bulk_list (pd.Series): a Panda Series with all Detections
            es_structure (elastic_model.Structure): a basic ElasticSearch
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

            body = [
                self.__get_bulk_string(t)
                for t in bulk_list[lower_limiter:higher_limiter]
            ]

            req = self.session.post(
                parse.urljoin(
                    es_structure.url, ''.join([es_structure.index, '/_bulk'])
                ),
                headers={'content-type': 'application/json'},
                data=''.join(body),
                verify=settings.VERIFY_SSL,
            )

            if req.status_code != 200:
                log = (
                    f'Elastic Search returned error inserting data. '
                    f'Status code: {req.status_code} ${req.text}'
                )
                logging.warning(log)
                raise ValueError(log)

            if req.json()['errors']:
                insertion_errors.extend(
                    [
                        {
                            'id': i['create']['_id'],
                            'error': i['create']['error']['reason'],
                            'caused': i['create']['error']['caused_by'],
                        }
                        for i in req.json()['items']
                        if i['create']['status'] == 400
                    ]
                )

        logger.info(f'[{datetime.now() - self.now}] Sent')
        return insertion_errors
