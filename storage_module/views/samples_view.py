from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from storage_module.models import DimBox, DimFacility, DimSample, DimSampleStatus, \
    DimSampleType, DimSourceFile
from storage_module.views.view_mixin import ViewMixin


class SamplesView(LoginRequiredMixin, ViewMixin, TemplateView):
    template_name = 'storage_module/samples.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        sample_type = self.request.GET.get('sample_type')
        box = self.request.GET.get('box')
        facility = self.request.GET.get('facility')
        row_number = int(self.request.POST.get('rows', 10))
        samples_list = self.get_samples_from_db(
            query=None, sample_type=None, box=None, facility=None)
        total_samples = len(samples_list)
        samples_list = self.get_samples_from_db(query, sample_type, box, facility)
        page_number = self.request.GET.get('page')
        paginator = Paginator(samples_list, row_number)

        context.update(
            samples=paginator.get_page(page_number),
            sample_statuses=self.sample_statuses,
            sample_types=self.sample_types,
            boxes=self.boxes,
            facilities=self.facilities,
            source_files=self.source_files,
            total_samples=total_samples,
            rows_options=[10, 25, 50, 100, 1000, 10000],
        )
        return context

    @property
    def sample_statuses(self):
        return DimSampleStatus.objects.all()

    @property
    def sample_types(self):
        return list(set(DimSampleType.objects.values_list('sample_type', flat=True)))

    @property
    def boxes(self):
        return list(set(DimBox.objects.values_list('box_name', flat=True)))

    @property
    def facilities(self):
        return list(set(DimFacility.objects.values_list('facility_name', flat=True)))

    @property
    def source_files(self):
        return list(set(DimSourceFile.objects.values_list('source_file_name', flat=True)))

    def post(self, request, *args, **kwargs):
        sample_ids = request.POST.getlist('sample_id')
        action = request.POST.get('action')
        if action == "export":
            return self.export_samples_as_csv(sample_ids)
        elif action and int(action) in self.sample_statuses.values_list('id', flat=True):
            for sample_id in sample_ids:
                sample = get_object_or_404(DimSample, sample_id=sample_id)
                new_status = get_object_or_404(DimSampleStatus, id=action)
                sample.sample_status = new_status
                sample.save()
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        sample_id = request.GET.get('sample_id', None)
        new_status_id = request.GET.get('sample_status', None)
        if sample_id and new_status_id:
            sample = get_object_or_404(DimSample, sample_id=sample_id)
            new_status = get_object_or_404(DimSampleStatus, id=new_status_id)
            sample.sample_status = new_status
            sample.save()
        return self.render_to_response(context)

    @staticmethod
    def get_samples_from_db(query=None, sample_type=None, box=None, facility=None):
        queryset = DimSample.objects.values(
            'sample_id',
            'sample_type__sample_type',
            'box_position__box__freezer__facility__facility_name',
            'box_position__box__freezer__facility__id',
            'source_file__source_file_name',
            'box_position__box__box_name',
            'box_position__box__id',
            'date_sampled',
            'sample_status__name'
        )
        if query:
            queryset = queryset.filter(sample_id__icontains=query)
        if sample_type and sample_type != 'all':
            queryset = queryset.filter(sample_type__sample_type=sample_type)
        if box and box != 'all':
            queryset = queryset.filter(box_position__box__box_name=box)
        if facility and facility != 'all':
            queryset = queryset.filter(
                box_position__box__freezer__facility__facility_name=facility)
        return queryset
