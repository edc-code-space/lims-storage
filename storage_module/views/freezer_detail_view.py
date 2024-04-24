from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..forms import MoveBoxForm
from ..models import (BoxPosition, DimFreezer)


class FreezerDetailView(DetailView):
    model = DimFreezer
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        freezer_id = self.kwargs.get('freezer_id')
        return get_object_or_404(DimFreezer, id=freezer_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            freezer = self.get_object()
            box = freezer.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        freezer = self.object
        boxes = freezer.boxes.all()
        move_box_form = MoveBoxForm()

        freezer_data = {}
        total_samples = BoxPosition.objects.count()

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

        context['inside_freezer'] = box_n_shelves_n_racks_data
        context['type'] = 'Freezer'
        context['name'] = freezer.freezer_name
        context['obj'] = freezer
        context['icon'] = 'fas fa-snowflake'
        context['facility'] = freezer.facility

        return context
