import os
import pandas as pd

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

from soy import utils

from .recipes import Recipes


class TestSoy(TestCase):

    @classmethod
    def setUpClass(cls):
        """Clear index test inside ElasticSearch server."""
        cls.client = APIClient()
        cls.upload_url = reverse('soy:upload-soy')
        cls.create_url = reverse('soy:create-soy')
        cls.delete_url = reverse('soy:delete-soy')

        cls.soy_error_file = settings.SOY_ERROR_TEST_URL
        cls.soy_success_file = settings.SOY_TEST_URL
        cls.soy_unexpected_file_url = os.path.join(
            'http://dawdawd.ad.awd/', 'tpeoinhRONWORIng.13d1d0')

        cls.recipes = Recipes()
        cls.es_structure = cls.recipes.es_object.make()

    @classmethod
    def tearDownClass(cls):
        """Clear index test inside ElasticSearch server."""
        cls.client.delete(cls.delete_url)

    def test_upload_no_file(self):
        """Tests if no file is sent."""
        response = self.client.post(self.upload_url)
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEquals(
            'File not found. No url file were sent', response.json()['msg']
        )

    def test_upload_error_file(self):
        """
        Tests if an json file with error is sent and a error is returned.
        """
        response = self.client.post(
            self.upload_url, {'file': self.soy_error_file})

        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEquals(
            'Unexpected sent text data. File has not the expected structure.',
            response.json()['msg']
        )

    def test_wrong_url(self):
        """Tests if a wrong url is sent"""

        response = self.client.post(
            self.upload_url, {'file': self.soy_unexpected_file_url})

        self.assertTrue(status.is_client_error(response.status_code))
        self.assertIn("File not found", response.json()['msg'])

    def test_verify_if_file_is_serialized(self):
        """Tests equality between serialized data and sent json file."""
        util_class = utils.Utils()
        txt = util_class.load_soy_file(self.soy_success_file)
        series = util_class.serialize_soy_file(txt)

        # Verifies if returned data is a Series type.
        self.assertIsInstance(series, pd.Series)

        # Verifies if returned data has same lenght as data sent.
        self.assertEqual(series.size, len(txt) / 2)

    def test_clear_detection_structure(self):
        """Tests if clear detection structure is safely deleted."""
        response = self.client.delete(self.delete_url)
        self.assertTrue(status.is_success(response.status_code))

    def test_create_detection_structure(self):
        """Tests if clear detection structure is safely created."""
        response = self.client.put(self.create_url)
        self.assertTrue(status.is_success(response.status_code))
