import json
import os
import pandas as pd
import yaml

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .recipes import Recipes

from core.views import UpdateDetectionView, UtilFunctions
from core.serializers import DetectionSerializer


class TestDetection(TestCase):
    def setUp(self):
        """Setp up test function."""
        self.client = APIClient()
        self.upload_url = reverse('upload-detection')
        self.create_url = reverse('create-detection')
        self.delete_url = reverse('delete-detection')
        self.json_data = json.loads(
            open("core/tests/mockData.json").read()
        )
        self.recipes = Recipes()

    def test_upload_no_file(self):
        """Tests if no file is sent."""
        response = self.client.post(self.upload_url)
        self.assertTrue(status.is_client_error(response.status_code))

    def test_upload_error_file(self):
        """Tests if an json file with error is sent."""
        self.recipes.es_object.make()
        response = {}

        with open('core/tests/mockDataWithError.json') as file:
            response = self.client.post(self.upload_url, {'file': file})

        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            'Unexpected sent json data', response.json()['msg'])

    def test_verify_if_file_is_serialized(self):
        """Test data return by bulk function being a list."""
        with open('core/tests/mockData.json') as json_file:
            js = json.loads(json_file.read())
            series = UtilFunctions.serialize_detection_file(js)

        self.assertIsInstance(series, pd.Series)

        self.assertEqual(series.size, len(js['features']))

    def test_clear_detection_structure(self):
        self.recipes.es_object.make()
        response = self.client.delete(self.delete_url)
        self.assertTrue(status.is_success(response.status_code))

    def test_create_detection_structure(self):
        self.recipes.es_object.make()
        response = self.client.put(self.create_url)
        self.assertTrue(status.is_success(response.status_code))

    # def test_size_of_features_and_bulk(self):
    #     """Test bulk list and and feature list have the same size."""
    #     bulk_list = ElasticSearch._populate_es_bulk_request(
    #         self.json_data['features'])

    #     self.assertEqual(
    #         len(self.json_data['features']), len(bulk_list))

    # def test_id_creation(self):
    #     """Test bulk list and and feature list have the same size."""
    #     bulk_list = ElasticSearch._populate_es_bulk_request(
    #         self.json_data['features'])

    #     id_feature_list = [f['properties']['id']
    #                        for f in self.json_data['features']]

    #     for bulk_element in bulk_list:
    #         """Testing if all ids were sent to update."""
    #         ids_inside_bulk_element = list(filter(lambda id: str(
    #             id) in bulk_element, id_feature_list))

    #         self.assertTrue(ids_inside_bulk_element)

    # def test_field_mapping(self):
    #     """Test bulk list has all defined fields."""
    #     bulk_list = ElasticSearch._populate_es_bulk_request(
    #         self.json_data['features'])

    #     for bulk_element in bulk_list:
    #         """Testing if all fields appear in the bulk query."""
    #         for f in ElasticSearch.list_of_fields:
    #             self.assertIn(f, bulk_element)

    # def test_file_structure_exists(self):
    #     """Tests if ES file mapping structure exists."""
    #     self.assertTrue(os.path.exists(
    #         'elasticsearch/detection_structure.json'))
