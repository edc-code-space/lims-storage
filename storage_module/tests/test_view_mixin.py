import os
import unittest
from unittest.mock import MagicMock, Mock, patch

import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'storage_module.settings'
django.setup()

from django import forms
from django.http import HttpRequest
from storage_module.models import DimBox
from storage_module.views.view_mixin import BaseStorageDetailView


class TestBaseStorageDetailView(unittest.TestCase):

    def setUp(self):
        self.view = BaseStorageDetailView()
        self.view.kwargs = {}
        self.view.model = Mock()
        self.view.lookup_id = 123
        self.view.storage_type = 'TestStorageType'
        self.view.storage_icon = 'TestIcon'
        self.request = HttpRequest()
        self.form_data = {'box_id': 1, 'freezer': 'Freezer1', 'shelf': 'Shelf1',
                          'rack': 'Rack1'}
        self.form = forms.Form(self.form_data)

    @patch('storage_module.views.view_mixin.get_object_or_404')
    def test_get_object(self, mock_get_object_or_404):
        self.view.get_object()
        mock_get_object_or_404.assert_called_once_with(self.view.model,
                                                       id=self.view.kwargs.get(
                                                           self.view.lookup_id))

    @patch('storage_module.views.view_mixin.MoveBoxForm')
    def test_post_valid_form(self, mock_form):
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = self.form_data
        self.view.process_form = MagicMock()
        self.view.get_containers = MagicMock(return_value=[])

        self.view.request = self.request

        with patch.object(BaseStorageDetailView, 'render_to_response',
                          return_value='mock_response') as mock_render_to_response:
            self.assertEqual(self.view.post(self.request),
                             'mock_response')
            self.view.process_form.assert_called_once()

    def test_process_form(self):
        mock_storage = Mock(boxes=Mock(get=Mock()))
        mock_box = Mock()
        mock_storage.boxes.get.return_value = mock_box
        self.view.get_object = MagicMock(return_value=mock_storage)
        self.request.POST = self.form_data
        self.form.cleaned_data = self.form_data
        self.view.process_form(self.request, self.form)
        mock_storage.boxes.get.assert_called_with(id=self.request.POST['box_id'])
        mock_storage.boxes.get.return_value.save.assert_called()

    @patch('storage_module.views.view_mixin.super')
    def test_get_context_data(self, mock_super):
        self.view.get_facility = MagicMock(return_value='TestFacility')
        self.view.build_display_data = MagicMock(return_value=[])
        self.view.object = MagicMock()
        mock_super().get_context_data.return_value = {}
        result = self.view.get_context_data()
        self.assertTrue('percent_filled' in result)
        self.assertTrue('type' in result)
        self.assertTrue('name' in result)
        self.assertTrue('obj' in result)
        self.assertTrue('icon' in result)
        self.assertTrue('facility' in result)
        self.assertTrue('total_samples' in result)
        self.assertTrue('total_capacity' in result)
        self.assertTrue('inside_freezer' in result)

    def test_build_display_data(self):
        self.view.get_containers = MagicMock(return_value=[])
        self.view.get_container_data = MagicMock(return_value=[])
        self.view.build_display_data()

    def test_get_containers_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.view.get_containers()

    def test_get_container_data(self):
        mock_objs = [DimBox(box_capacity=5)]
        self.view.get_container_data('box', mock_objs, 'icon')

    def test_get_facility_with_freezer(self):
        mock_storage = Mock(freezer=Mock(facility=Mock()))
        result = self.view.get_facility(mock_storage)
        self.assertIsNotNone(result)

    def test_get_facility_with_shelf(self):
        mock_storage = Mock(freezer=None, shelf=Mock(freezer=Mock(facility=Mock())))
        result = self.view.get_facility(mock_storage)
        self.assertIsNotNone(result)

    def test_get_facility_with_nither(self):
        mock_storage = Mock(freezer=None, shelf=None)
        result = self.view.get_facility(mock_storage)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
