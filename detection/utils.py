import logging
import json
import pandas as pd

from datetime import datetime
from json.decoder import JSONDecodeError

from detection import serializers, models
from elastic import utils


logger = logging.getLogger('django')


class Utils(utils.Utils):
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
            serializer = serializers.DetectionSerializer(
                data=json_file['features'], many=True
            )
            serializer.is_valid(raise_exception=True)
            logger.info(f'[{datetime.now() - self.now}] Serialized!')
            return self.__create_detection_series(serializer.validated_data)
        except Exception as exc:
            log = f'Internal error: {str(exc)}'
            logger.warning(log)
            raise ValueError(log)

    def load_detection_file(self, file_url: str) -> object:
        """Loads a uploaded json file into a json object.

        Args:
            file_url (str): url for file download

        Raises:
            ValueError: Raises error if its not possible to parse Json File

        Returns:
            object: Json Object parsed
        """
        try:
            file_content = self._download_file_from_url(file_url, '.geojson')
            return json.loads(file_content.read())
        except JSONDecodeError:
            log = f'Unexpected sent json data.'
            logger.warning(log)
            raise ValueError(log)
        except Exception:
            log = f'File not found.'
            logger.warning(log)
            raise ValueError(log)

    def __create_detection_series(self, data: object) -> pd.Series:
        """Creates a Panda Series with a serialized data.

        Args:
            data (object): Serialized and validated Json data

        Returns:
            pd.Series: returns a Panda Series with all Detection Models
        """
        logger.info(f'[{datetime.now() - self.now}] creating series....')

        pd_detections = pd.Series(
            [models.Detection(**value) for value in data])

        logger.info(f'[{datetime.now() - self.now}] series created!')
        return pd_detections

    def __get_bulk_string(self, element: object) -> str:
        """Internal method for getting the bulk data.

        It separates between Soy and Detection since both file have
        a different structure

        Args:
            element (object): the element to get its bulk
            es_structure ([type]): type of Structure we're dealing with
                (Soy or Detection)

        Returns:
            str: Returns the bulk line for that element
        """
        return element.get_es_insertion_line()
