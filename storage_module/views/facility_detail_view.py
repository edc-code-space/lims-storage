from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..models import (BoxPosition, DimBox, DimFacility)


class FacilityDetailView(DetailView):
    model = DimFacility
    template_name = "storage_module/facility_detail.html"
    context_object_name = "facility"
    slug_field = "facility_name"
    slug_url_kwarg = "facility_name"

    def get_object(self, queryset=None):
        facility_id = self.kwargs.get('facility_id')
        return get_object_or_404(DimFacility, id=facility_id)

    def _aggregate_boxes(self, boxes, url, icon):
        capacity = 0
        stored_samples = 0
        aggregated_boxes = []

        for box in boxes:
            samples_in_box = BoxPosition.objects.filter(box=box).count()
            if samples_in_box > 0:
                capacity += box.box_capacity
                stored_samples += samples_in_box

                _box = {
                    'id': box.id,
                    'url': url,
                    'icon': icon,
                    'name': box.box_name,
                    'capacity': box.box_capacity,
                    'stored_samples': samples_in_box,
                }

                aggregated_boxes.append(_box)

        return aggregated_boxes, capacity, stored_samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        facility = self.object
        facility_data = []

        for freezer in facility.dimfreezer_set.all():
            boxes = DimBox.objects.filter(
                Q(shelf__freezer=freezer) |
                Q(rack__shelf__freezer=freezer) |
                Q(rack__freezer=freezer) |
                Q(freezer=freezer)
            )

            freezer_data = {'freezer': freezer}
            box_n_shelves_n_racks_data = []
            freezer_total_samples = 0
            freezer_total_capacity = sum(box.box_capacity for box in boxes)
            selected_box_ids = freezer.boxes.all().values_list('id', flat=True)

            for box in boxes:
                freezer_total_samples += len(box.get_samples())

            aggregated_boxes, _, _ = self._aggregate_boxes(
                freezer.boxes.filter(shelf=None, rack=None), 'box_detail', 'fas fa-cube')
            box_n_shelves_n_racks_data += aggregated_boxes

            for shelf in freezer.shelves.all():
                aggregated_boxes, capacity, stored_samples = self._aggregate_boxes(
                    shelf.boxes.all(), 'shelf_detail', 'fas fa-layer-group')
                box_n_shelves_n_racks_data += aggregated_boxes

                _shelf = {
                    'id': shelf.id,
                    'url': 'shelf_detail',
                    'icon': 'fas fa-layer-group',
                    'name': shelf.shelf_name,
                    'capacity': capacity,
                    'stored_samples': stored_samples
                }

                box_n_shelves_n_racks_data += [_shelf]

            for rack in freezer.racks.all():
                aggregated_boxes, capacity, stored_samples = self._aggregate_boxes(
                    rack.boxes.all(), 'rack_detail', 'fas fa-box-open')
                box_n_shelves_n_racks_data += aggregated_boxes

                _rack = {
                    'id': rack.id,
                    'url': 'rack_detail',
                    'icon': 'fas fa-box-open',
                    'name': rack.rack_name,
                    'capacity': capacity,
                    'stored_samples': stored_samples
                }

                box_n_shelves_n_racks_data += [_rack]

            freezer_data.update(
                inside_freezer=box_n_shelves_n_racks_data,
                freezer_total_capacity=freezer_total_capacity,
                freezer_total_samples=freezer_total_samples
            )

            facility_data.append(freezer_data)

        context['facility_data'] = facility_data
        return context
