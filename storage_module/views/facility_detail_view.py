from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import DetailView

from ..models import BoxPosition, DimBox, DimFacility


class FacilityDetailView(LoginRequiredMixin, DetailView):
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
                _box = self._create_dict(box.id, url, icon, box.box_name,
                                         box.box_capacity, samples_in_box)
                aggregated_boxes.append(_box)

        return aggregated_boxes, capacity, stored_samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        facility = self.object
        facility_data = []

        context['cardsHTML'] = ''
        context['tableHTML'] = ''

        for freezer in facility.dimfreezer_set.all():
            boxes = DimBox.objects.filter(
                Q(shelf__freezer=freezer) |
                Q(rack__shelf__freezer=freezer) |
                Q(rack__freezer=freezer) |
                Q(freezer=freezer)
            )
            freezer_data = {'freezer': freezer}
            box_n_shelves_n_racks_data = []
            freezer_aggregated_boxes = []
            freezer_stored_samples = 0

            selected_box_ids = freezer.boxes.all().values_list('id', flat=True)

            aggregated_boxes, aggregated_boxes_capacity, aggregated_boxes_samples = (
                self._aggregate_boxes(freezer.boxes.filter(shelf=None, rack=None),
                                      'box_detail', 'fas fa-cube'))
            box_n_shelves_n_racks_data += aggregated_boxes
            freezer_aggregated_boxes += aggregated_boxes
            freezer_stored_samples += aggregated_boxes_samples
            for shelf in freezer.shelves.all():
                aggregated_boxes, capacity, stored_samples = self._aggregate_boxes(
                    shelf.boxes.all(), 'shelf_detail', 'fas fa-layer-group')
                box_n_shelves_n_racks_data += aggregated_boxes
                freezer_aggregated_boxes += aggregated_boxes
                freezer_stored_samples += stored_samples
                box_n_shelves_n_racks_data.append(
                    self._create_dict(shelf.id, 'shelf_detail', 'fas fa-layer-group',
                                      shelf.shelf_name, capacity, stored_samples))
            for rack in freezer.racks.all():
                aggregated_boxes, capacity, stored_samples = self._aggregate_boxes(
                    rack.boxes.all(), 'rack_detail', 'fas fa-box-open')
                box_n_shelves_n_racks_data += aggregated_boxes
                freezer_aggregated_boxes += aggregated_boxes
                freezer_stored_samples += stored_samples
                box_n_shelves_n_racks_data.append(
                    self._create_dict(rack.id, 'rack_detail', 'fas fa-box-open',
                                      rack.rack_name, capacity, stored_samples))

            freezer_total_capacity = sum(
                box.get('capacity', 0) for box in freezer_aggregated_boxes)

            freezer_total_samples = round(
                ((freezer_stored_samples / freezer_total_capacity)
                 * 100), 1) if freezer_total_capacity else 0
            freezer_data.update(
                inside_freezer=box_n_shelves_n_racks_data,
                freezer_total_capacity=freezer_total_capacity,
                freezer_total_samples=freezer_total_samples,
                freezer_stored_samples=freezer_stored_samples,
                aggregated_capacity=len(freezer_aggregated_boxes),
            )

            facility_data.append(freezer_data)

        cardsHTML = render_to_string('storage_module/card_fragment.html',
                                     {'facility_data': facility_data})
        tableHTML = render_to_string('storage_module/table_fragment.html',
                                     {'facility_data': facility_data})

        context['cardsHTML'] += cardsHTML
        context['tableHTML'] += tableHTML

        return context

    def _create_dict(self, id, url, icon, name, capacity, stored_samples):
        return {
            'id': id,
            'url': url,
            'icon': icon,
            'name': name,
            'capacity': capacity,
            'stored_samples': stored_samples
        }
