import json
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.views import UpdateDetectionView


class TestDetection(TestCase):

    @classmethod
    def setUpClass(cls):
        """Setp up test function."""
        cls.client = APIClient()
        cls.url = reverse('es:load-es')
        cls.json_data = json.loads(
            open("elasticsearch/tests/mockData.json").read()
        )

    def test_upload_no_file(self):
        """Tests if no file is sent."""
        response = self.client.post(self.url)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_upload_error_file(self):
        """Tests if an json file with error is sent."""
        with open("elasticsearch/tests/mockDataWithError.json") as file:
            with self.assertRaises(ValueError) as exception:
                ElasticSearch.loadDetections(file)

        self.assertTrue(
            'Unexpected sent json data' in str(exception.exception))

    def test_populate_bulk_request(self):
        """Test data return by bulk function being a list."""
        bulk_list = ElasticSearch._populate_es_bulk_request(
            self.json_data['features'])

        self.assertIsInstance(bulk_list, list)

    def test_size_of_features_and_bulk(self):
        """Test bulk list and and feature list have the same size."""
        bulk_list = ElasticSearch._populate_es_bulk_request(
            self.json_data['features'])

        self.assertEqual(
            len(self.json_data['features']), len(bulk_list))

    def test_id_creation(self):
        """Test bulk list and and feature list have the same size."""
        bulk_list = ElasticSearch._populate_es_bulk_request(
            self.json_data['features'])

        id_feature_list = [f['properties']['id']
                           for f in self.json_data['features']]

        for bulk_element in bulk_list:
            """Testing if all ids were sent to update."""
            ids_inside_bulk_element = list(filter(lambda id: str(
                id) in bulk_element, id_feature_list))

            self.assertTrue(ids_inside_bulk_element)

    def test_field_mapping(self):
        """Test bulk list has all defined fields."""
        bulk_list = ElasticSearch._populate_es_bulk_request(
            self.json_data['features'])

        for bulk_element in bulk_list:
            """Testing if all fields appear in the bulk query."""
            for f in ElasticSearch.list_of_fields:
                self.assertIn(f, bulk_element)

    def test_file_structure_exists(self):
        """Tests if ES file mapping structure exists."""
        self.assertTrue(os.path.exists(
            'elasticsearch/detection_structure.json'))
