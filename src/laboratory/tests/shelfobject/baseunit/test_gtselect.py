
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from unittest.mock import MagicMock, patch
from laboratory.models import Catalog
from laboratory.gtselects import CatalogUnitLookup


class CatalogUnitLookupTest(TestCase):
    def setUp(self):
        super().setUp()
        self.org = self.org1
        self.lab = self.lab1_org1
        self.user = self.user1_org1
        self.catalog1 = Catalog.objects.create(description='Unit 1', key='units')
        self.catalog2 = Catalog.objects.create(description='Unit 2', key='other')

        self.lookup_view = reverse('catalogunit-list')
        self.lookup_view.shelf = MagicMock()
        self.lookup_view.shelf.measurement_unit = None

    def test_get_queryset_with_shelf_and_measurement_unit(self):
        self.lookup_view.shelf.measurement_unit = 'some_unit'
        with patch('laboratory.utils_base_unit.get_related_units', return_value=[self.catalog1]):
            queryset = self.lookup_view.get_queryset()
            self.assertIn(self.catalog1, queryset)
            self.assertNotIn(self.catalog2, queryset)

    def test_get_queryset_with_shelf_without_measurement_unit(self):
        self.lookup_view.shelf.measurement_unit = None
        queryset = self.lookup_view.get_queryset()
        self.assertQuerysetEqual(queryset, [])

    def test_get_queryset_without_shelf(self):
        self.lookup_view.shelf = None
        queryset = self.lookup_view.get_queryset()
        self.assertQuerysetEqual(queryset, [])
