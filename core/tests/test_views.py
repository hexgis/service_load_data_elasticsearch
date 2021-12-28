import json
import os
import pandas as pd

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.views import UtilFunctions
from .recipes import Recipes


class TestDetection(TestCase):
    @classmethod
    def setUpClass(cls):
        """Clear index test inside ElasticSearch server."""
        cls.client = APIClient()
        cls.upload_url = reverse('core:upload-detection')
        cls.create_url = reverse('core:create-detection')
        cls.delete_url = reverse('core:delete-detection')
        cls.recipes = Recipes()
        cls.es_structure = cls.recipes.es_object.make()

    @classmethod
    def tearDownClass(cls):
        """Clear index test inside ElasticSearch server."""
        client = APIClient()
        delete_url = reverse('core:delete-detection')
        client.delete(delete_url)

    def test_upload_no_file(self):
        """Tests if no file is sent."""
        response = self.client.post(self.upload_url)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_upload_error_file(self):
        """
        Tests if an json file with error is sent and a error is returned.
        """

        with open('core/tests/mockDataWithError.json') as file:
            response = self.client.post(self.upload_url, {'file': file})

        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            'Unexpected sent json data', response.json()['msg'])

    def test_verify_if_file_is_serialized(self):
        """Tests equality between serialized data and sent json file."""
        with open('core/tests/mockData.json') as json_file:
            js = json.loads(json_file.read())
            util_class = UtilFunctions()
            series = util_class.serialize_detection_file(js)

        # Verifies if returned data is a Series type.
        self.assertIsInstance(series, pd.Series)

        # Verifies if returned data has same lenght as data sent.
        self.assertEqual(series.size, len(js['features']))

        # Verifies if returned data has same ids sent for serializing.
        id_feature_list = [f['properties']['id']
                           for f in js['features']]

        for element in series:
            # Testing if all ids were sent to update.
            ids_inside_bulk_element = list(
                filter(lambda id: id == element._id, id_feature_list))

            self.assertTrue(ids_inside_bulk_element)

        # Verifies if all fields inside ES Structure were serialized on
        # the object.
        detection_structure = json.loads(
            self.es_structure.structure)

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

    def test_fixture_file_exists(self):
        """Tests if ES file mapping structure exists."""
        self.assertTrue(os.path.exists(
            'core/fixtures/es_structure.yaml'))
