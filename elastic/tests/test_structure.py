import os

from django.test import TestCase


class TestElastic(TestCase):

    def test_fixture_file_exists(self):
        """Tests if ES file mapping structure exists."""
        self.assertTrue(os.path.exists('elastic/fixtures/es_structure.yaml'))
