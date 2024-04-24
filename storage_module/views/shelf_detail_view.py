from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..forms import MoveBoxForm
from ..models import (BoxPosition, DimShelf)


class ShelfDetailView(DetailView):
    model = DimShelf
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        shelf_id = self.kwargs.get('shelf_id')
        return get_object_or_404(DimShelf, id=shelf_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            shelf = self.get_object()
            box = shelf.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shelf = self.object
        boxes = shelf.boxes.all()
        move_box_form = MoveBoxForm()

        box_n_shelves_n_racks_data = []
        for box in shelf.boxes.filter(rack=None):
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

        for rack in shelf.racks.all():
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
        context['type'] = 'Shelf'
        context['name'] = shelf.shelf_name
        context['obj'] = shelf
        context['icon'] = 'fas fa-layer-group'
        context['facility'] = shelf.freezer.facility

        return context
