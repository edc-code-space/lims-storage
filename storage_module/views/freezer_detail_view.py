from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ..forms import MoveBoxForm
from ..models import (BoxPosition, DimBox, DimFreezer, DimRack, DimShelf)


class FreezerDetailView(LoginRequiredMixin, DetailView):
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

        context['inside_freezer'] = self.get_container_data('box', 'boxes', 'fas fa-cube')
        context['inside_freezer'].extend(
            self.get_container_data('shelf', 'shelves', 'fas fa-layer-group'))
        context['inside_freezer'].extend(
            self.get_container_data('rack', 'racks', 'fas fa-box-open'))

        context['type'] = 'Freezer'
        context['name'] = freezer.freezer_name
        context['obj'] = freezer
        context['icon'] = 'fas fa-snowflake'
        context['facility'] = freezer.facility

        return context

    def get_container_data(self, container_type, queryset_method, icon, ):
        container_data = []
        freezer = self.object
        for container in getattr(freezer, queryset_method).all():
            if isinstance(container, DimBox):
                capacity = container.box_capacity
                samples_in_container = {'box': container}
            else:
                capacity = container.boxes.aggregate(total_capacity=Sum('box_capacity'))[
                    'total_capacity']
                if isinstance(container, DimRack):
                    samples_in_container = {'box__rack': container}
                if isinstance(container, DimShelf):
                    samples_in_container = {'box__shelf': container}
            samples = BoxPosition.objects.filter(**samples_in_container).count()
            if samples > 0:
                name_field = f"{container_type}_name"
                container_data.append({
                    'id': container.id,
                    'url': f'{container_type}_detail',
                    'icon': icon,
                    'name': getattr(container, name_field),  # Dynamic attribute access
                    'capacity': capacity,
                    'stored_samples': samples
                })
        return container_data
