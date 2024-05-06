from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from storage_module.forms import MoveBoxForm
from storage_module.models import BoxPosition, DimRack


class RackDetailView(LoginRequiredMixin, DetailView):
    model = DimRack
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        rack_id = self.kwargs.get('rack_id')
        return get_object_or_404(DimRack, id=rack_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            self.process_form(request, form)
        return super().get(request, *args, **kwargs)

    def process_form(self, request, form):
        rack = self.get_object()
        box = rack.boxes.get(id=request.POST['box_id'])
        box.freezer = form.cleaned_data.get('freezer')
        box.shelf = form.cleaned_data.get('shelf')
        box.rack = form.cleaned_data.get('rack')
        box.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rack = self.object
        boxes = rack.boxes.all()
        context['inside_freezer'] = self.build_box_data(boxes)
        context.update({
            'type': 'rack',
            'name': rack.rack_name,
            'obj': rack,
            'icon': 'fas fa-box-open',
            'facility': self.get_facility(rack, boxes)
        })
        return context

    def build_box_data(self, boxes):
        box_data = []
        for box in boxes:
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
                box_data.append(_box)
        return box_data

    def get_facility(self, rack, boxes):
        facility = None
        if rack.freezer:
            facility = getattr(rack, 'freezer').facility
        elif rack.shelf:
            facility = getattr(rack, 'shelf').freezer.facility
        elif boxes:
            facility = boxes[0].facility
        return facility
