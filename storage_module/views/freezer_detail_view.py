from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..forms import MoveBoxForm
from ..models import (BoxPosition, DimFreezer)


class FreezerDetailView(DetailView):
    model = DimFreezer
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(DimFreezer, id=self.kwargs.get('freezer_id'))

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            self.move_box_using_form_data(form)
        return super().get(request, *args, **kwargs)

    def move_box_using_form_data(self, form):
        box = self.get_object().boxes.get(id=self.request.POST['box_id'])
        box.freezer = form.cleaned_data['freezer']
        box.shelf = form.cleaned_data['shelf']
        box.rack = form.cleaned_data['rack']
        box.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        freezer = self.object
        context['inside_freezer'] = self.get_inside_freezer_data(freezer)
        context.update({
            'type': 'Freezer',
            'name': freezer.freezer_name,
            'obj': freezer,
            'icon': 'fas fa-snowflake',
            'facility': freezer.facility,
        })
        return context

    def get_inside_freezer_data(self, freezer):
        data = []
        for element, url, icon in [
            (freezer.boxes.filter(shelf=None, rack=None), 'box_detail', 'fas fa-cube'),
            (freezer.shelves.all(), 'shelf_detail', 'fas fa-layer-group'),
            (freezer.racks.all(), 'rack_detail', 'fas fa-box-open')]:
            data.extend(self.get_element_data(element, url, icon))
        return data

    @staticmethod
    def get_element_data(element, url, icon):
        result = []
        for e in element:
            samples_in_element = BoxPosition.objects.filter(box=e).count()
            if samples_in_element > 0:
                data = {
                    'id': e.id,
                    'url': url,
                    'icon': icon,
                    'name': getattr(e, f'{e.__class__.__name__.lower()}_name'),
                    'capacity': getattr(e, f'{e.__class__.__name__.lower()}_capacity', 0),
                    'stored_samples': samples_in_element,
                }
                result.append(data)
        return result
