from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView

from storage_module.barcode_printer_helper import BarcodePrinter
from storage_module.forms import MoveBoxForm
from storage_module.models import DimBox, DimSampleStatus, DimSampleType
from storage_module.util import update_sample_status
from storage_module.views.view_mixin import ViewMixin


class BoxDetailView(LoginRequiredMixin, ViewMixin, DetailView):
    model = DimBox
    template_name = 'storage_module/box_detail.html'

    def get_object(self, queryset=None):
        box_id = self.kwargs.get('box_id')
        return get_object_or_404(DimBox, id=box_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)

        action = request.POST.get('action')
        selected_samples = request.POST.getlist('sample_ids')

        if action == 'move':
            base_url = reverse('move_samples')
            query_string = urlencode({'sample_ids': ','.join(selected_samples)})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

        if action in self.sample_types:
            for sample_id in selected_samples:
                update_sample_status(sample_id=sample_id, status=action)

        if action == "export":
            return self.export_samples_as_csv(selected_samples)

        if action == 'print':
            printer = BarcodePrinter()
            printer.print_barcode_for_selected_samples(selected_samples)

        if form.is_valid():
            box = self.get_object()
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        box = self.object
        positions = box.positions.order_by('x_position', 'y_position')

        location = getattr(box, 'location', None)

        rack = location.get('rack', None)
        shelf = location.get('shelf', None)
        freezer = location.get('freezer', None)
        facility = location.get('facility', None)
        initial = {}
        if freezer:
            initial.update(freezer=freezer.id)
        if shelf:
            initial.update(shelf=shelf.id)
        if rack:
            initial.update(rack=rack.id)

        move_box_form = MoveBoxForm(
            initial=initial
        )

        x_labels = [int(i) for i in range(1, 10)]
        y_labels = [chr(i) for i in range(ord('A'), ord('J'))]

        context.update(
            box=box,
            positions=positions,
            rack=rack,
            shelf=shelf,
            freezer=freezer,
            facility=facility,
            move_box_form=move_box_form,
            x_labels=x_labels,
            y_labels=y_labels,
            sample_statuses=self.sample_statuses,
            sample_types=self.sample_types,
        )

        return context

    @property
    def sample_statuses(self):
        return DimSampleStatus.objects.all()

    @property
    def sample_types(self):
        return list(set(DimSampleType.objects.values_list('sample_type', flat=True)))
