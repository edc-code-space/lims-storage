from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..models import (BoxPosition, DimFacility)


class FacilityDetailView(DetailView):
    model = DimFacility
    template_name = "storage_module/facility_detail.html"
    context_object_name = "facility"
    slug_field = "facility_name"
    slug_url_kwarg = "facility_name"

    def get_object(self, queryset=None):
        facility_id = self.kwargs.get('facility_id')
        return get_object_or_404(DimFacility, id=facility_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facility = self.object
        facility_data = []
        total_samples = BoxPosition.objects.count()

        for freezer in facility.dimfreezer_set.all():
            freezer_data = {'freezer': freezer}
            freezer_total_capacity = freezer.boxes.aggregate(Sum('box_capacity'))[
                'box_capacity__sum']
            selected_box_ids = freezer.boxes.all().values_list('id', flat=True)
            freezer_total_samples = BoxPosition.objects.filter(
                box__id__in=selected_box_ids).count()

            box_n_shelves_n_racks_data = []
            for box in freezer.boxes.filter(shelf=None, rack=None):
                samples_in_box = BoxPosition.objects.filter(box=box).count()
                if samples_in_box > 0:
                    _box = {
                        'id': box.id,
                        'url': 'box_detail',
                        'icon': 'fas fa-cube',
                        'name': box.box_name,
                        'capacity': box.box_capacity,
                        'stored_samples': samples_in_box,
                    }
                    box_n_shelves_n_racks_data.append(_box)

            for shelf in freezer.shelves.all():
                boxes_on_shelf = shelf.boxes.all()
                capacity = 0
                boxes_on_shelf_samples = 0
                for box in boxes_on_shelf:
                    boxes_on_shelf_samples = BoxPosition.objects.filter(box=box).count()
                    if boxes_on_shelf_samples > 0:
                        capacity += box.box_capacity
                _shelf = {
                    'id': shelf.id,
                    'url': 'shelf_detail',
                    'icon': 'fas fa-layer-group',
                    'name': shelf.shelf_name,
                    'capacity': capacity,
                    'stored_samples': boxes_on_shelf_samples
                }
                box_n_shelves_n_racks_data.append(_shelf)

            for rack in freezer.racks.all():
                boxes_on_rack = rack.boxes.all()
                capacity = 0
                boxes_on_rack_samples = 0
                for box in boxes_on_rack:
                    boxes_on_rack_samples = BoxPosition.objects.filter(box=box).count()
                    if boxes_on_rack_samples > 0:
                        capacity += box.box_capacity
                _rack = {
                    'id': rack.id,
                    'url': 'rack_detail',
                    'icon': 'fas fa-box-open',
                    'name': rack.rack_name,
                    'capacity': capacity,
                    'stored_samples': boxes_on_rack_samples
                }
                box_n_shelves_n_racks_data.append(_rack)

            freezer_data.update(
                inside_freezer=box_n_shelves_n_racks_data,
                freezer_total_capacity=freezer_total_capacity,
                freezer_total_samples=freezer_total_samples
            )

            facility_data.append(freezer_data)

        context['facility_data'] = facility_data
        return context
