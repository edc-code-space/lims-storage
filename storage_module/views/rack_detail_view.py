from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from storage_module.forms import MoveBoxForm
from storage_module.models import BoxPosition, DimRack


class RackDetailView(DetailView):
    model = DimRack
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        rack_id = self.kwargs.get('rack_id')
        return get_object_or_404(DimRack, id=rack_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            rack = self.get_object()
            box = rack.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rack = self.object
        boxes = rack.boxes.all()
        move_box_form = MoveBoxForm()

        facility = None
        if rack.freezer:
            facility = getattr(rack, 'freezer').facility
        elif rack.shelf:
            facility = getattr(rack, 'shelf').freezer.facility
        elif boxes:
            facility = boxes[0].facility

        box_n_shelves_n_racks_data = []
        for box in rack.boxes.all():
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

        context['inside_freezer'] = box_n_shelves_n_racks_data
        context['type'] = 'rack'
        context['name'] = rack.rack_name
        context['obj'] = rack
        context['icon'] = 'fas fa-box-open'
        context['facility'] = facility

        return context
