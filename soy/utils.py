import logging
import pandas as pd

from datetime import datetime

from elastic import utils


logger = logging.getLogger('django')


class Utils(utils.Utils):
    def serialize_soy_file(self, text_array_file: list) -> pd.Series:
        """Method for serializing a read array file into a panda Series.

        It follows the same flow as detection, so when it gets more complex,
        it just needs some adjustments.

        Args:
            text_array_file (list): The read file as an array,
                each element as a line

        Raises:
            ValueError: Raises error if it encounters and error

        Returns:
            pd.Series: A Panda Series with all bulk data needed for ES
        """
        logger.info(f'[{datetime.now() - self.now}] serializing....')

        try:
            logger.info(f'[{datetime.now() - self.now}] Serialized!')
            return self._create_soy_series(text_array_file)
        except Exception as exc:
            log = f'Internal error: {str(exc)}'
            logger.warning(log)
            raise ValueError(log)

    def load_soy_file(self, file_url: str) -> list:
        """Download soy file and loads it into memory.

        Args:
            file_url (str): Url string for downloading the file

        Raises:
            ValueError: Raises error if file is not found in the url

        Returns:
            object: Returns an list of all lines on the file
        """
        try:
            text_file = self._download_file_from_url(file_url, '.txt')
            return text_file.readlines()
        except Exception:
            log = f'File not found.'
            logger.warning(log)
            raise ValueError(log)

    def _create_soy_series(self, data: object) -> pd.Series:
        """Internal method for creating a Panda Series of Soy data.

        Args:
            data (object): The list of all the lines in the soy file

        Returns:
            pd.Series: A panda Series with all the bulk data, serialized
        """
        logger.info(f'[{datetime.now() - self.now}] creating series....')

        index_list = [value for key, value in enumerate(data) if not key % 2]
        value_list = [value for key, value in enumerate(data) if key % 2]

        pd_soy = pd.Series([f'{i}{v}' for i, v in zip(index_list, value_list)])

        logger.info(f'[{datetime.now() - self.now}] series created!')
        return pd_soy

    def _get_bulk_string(self, element: object) -> str:
        """Internal method for getting the bulk data.

        It separates between Soy and Detection since both file have
        a different structure

        Args:
            element (object): the element to get its bulk

        Returns:
            str: Returns the bulk line for that element
        """
        return element