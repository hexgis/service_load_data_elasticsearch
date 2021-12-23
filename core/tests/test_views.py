import json
import os
import pandas as pd

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.views import UtilFunctions
from .recipes import Recipes


class TestDetection(TestCase):
    def setUp(self):
        """Setp up test function."""
        self.client = APIClient()
        self.upload_url = reverse('upload-detection')
        self.create_url = reverse('create-detection')
        self.delete_url = reverse('delete-detection')
        self.recipes = Recipes()

    @classmethod
    def tearDownClass(cls):
        """Clear index test inside ElasticSearch server."""
        recipes = Recipes()
        recipes.es_object.make()
        client = APIClient()
        delete_url = reverse('delete-detection')
        client.delete(delete_url)

    def test_upload_no_file(self):
        """Tests if no file is sent."""
        response = self.client.post(self.upload_url)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_upload_error_file(self):
        """Tests if an json file with error is sent and a error is returned."""
        self.recipes.es_object.make()

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

        """Verifies if returned data is a Series type."""
        self.assertIsInstance(series, pd.Series)

        """Verifies if returned data has same lenght as data sent."""
        self.assertEqual(series.size, len(js['features']))

        """Verifies if returned data has same ids sent for serializing."""
        id_feature_list = [f['properties']['id']
                           for f in js['features']]

        for element in series:
            """Testing if all ids were sent to update."""
            ids_inside_bulk_element = list(
                filter(lambda id: id == element._id, id_feature_list))

            self.assertTrue(ids_inside_bulk_element)

        """Verifies if all fields inside ES Structure were serialized on
        the object."""
        es_structure = self.recipes.es_object.make()
        detection_structure = json.loads(
            es_structure.structure)

        for element in series:
            """Testing if all fields appear in the bulk query."""
            for f in detection_structure['mappings']['properties']:
                element_fields = [i.get_attname()
                                  for i in element._meta.get_fields()]
                self.assertIn(f, element_fields)

    def test_clear_detection_structure(self):
        """Tests if clear detection structure is safely deleted."""
        self.recipes.es_object.make()
        response = self.client.delete(self.delete_url)
        self.assertTrue(status.is_success(response.status_code))

    def test_create_detection_structure(self):
        """Tests if clear detection structure is safely created."""
        self.recipes.es_object.make()
        response = self.client.put(self.create_url)
        self.assertTrue(status.is_success(response.status_code))

    def test_fixture_file_exists(self):
        """Tests if ES file mapping structure exists."""
        self.assertTrue(os.path.exists(
            'core/fixtures/es_structure.yaml'))
