import json
import os
import pandas as pd

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.staticfiles import finders
from rest_framework.test import APIClient
from rest_framework import status

from detection import utils

from .recipes import Recipes


class TestDetection(TestCase):
    @classmethod
    def setUpClass(cls):
        """Clear index test inside ElasticSearch server."""
        cls.client = APIClient()
        cls.upload_url = reverse('detection:upload-detection')
        cls.create_url = reverse('detection:create-detection')
        cls.delete_url = reverse('detection:delete-detection')

        cls.detection_error_file = settings.DETECTION_ERROR_TEST_URL
        cls.detection_success_file = settings.DETECTION_TEST_URL
        cls.detection_unexpected_file_url = os.path.join(
            'http://fqfqasdf.ad.com/', 'tyjryj5.1r113ra')

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
            self.upload_url, {'file': self.detection_error_file})

        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEquals(
            'Unexpected sent json data.', response.json()['msg']
        )

    def test_wrong_url(self):
        """Tests if a wrong url is sent"""

        response = self.client.post(
            self.upload_url, {'file': self.detection_unexpected_file_url})

        self.assertTrue(status.is_client_error(response.status_code))
        self.assertIn("File not found", response.json()['msg'])

    def test_verify_if_file_is_serialized(self):
        """Tests equality between serialized data and sent json file."""

        util_class = utils.Utils()
        js = util_class.load_detection_file(self.detection_success_file)
        series = util_class.serialize_detection_file(js)

        # Verifies if returned data is a Series type.
        self.assertIsInstance(series, pd.Series)

        # Verifies if returned data has same lenght as data sent.
        self.assertEqual(series.size, len(js['features']))

        # Verifies if returned data has same ids sent for serializing.
        id_feature_list = [f['properties']['id'] for f in js['features']]

        for element in series:
            # Testing if all ids were sent to update.
            ids_inside_bulk_element = list(
                filter(lambda id: id == element._id, id_feature_list))

            self.assertTrue(ids_inside_bulk_element)

        # Verifies if all fields inside ES Structure were serialized on
        # the object.
        detection_structure = json.loads(self.es_structure.structure)

        for element in series:
            # Testing if all fields appear in the bulk query.
            for f in detection_structure['mappings']['properties']:
                element_fields = [i.get_attname()
                                  for i in element._meta.get_fields()]
                self.assertIn(f, element_fields)

    def test_clear_detection_structure(self):
        """Tests if clear detection structure is safely deleted."""
        response = self.client.delete(self.delete_url)
        self.assertTrue(status.is_success(response.status_code))

    def test_create_detection_structure(self):
        """Tests if clear detection structure is safely created."""
        response = self.client.put(self.create_url)
        self.assertTrue(status.is_success(response.status_code))
