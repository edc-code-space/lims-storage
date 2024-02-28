from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .models import DimSample, DimSampleStatus


class HomeView(TemplateView):
    template_name = 'storage_module/home.html'


class SamplesView(TemplateView):
    template_name = 'storage_module/samples.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        samples_list = self.get_samples_from_db(query)
        page_number = self.request.GET.get('page')
        paginator = Paginator(samples_list, 10)
        sample_statuses = DimSampleStatus.objects.all()

        context.update(
            samples=paginator.get_page(page_number),
            sample_statuses=sample_statuses
        )

        return context

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
    def get_samples_from_db(query=None):
        queryset = DimSample.objects.values(
            'sample_id',
            'sample_type__sample_type',
            'facility__facility_name',
            'source_file__source_file_name',
            'box__box_name',
            'time__time_sampled',
            'sample_status__name'
        )
        if query:
            queryset = queryset.filter(sample_id__icontains=query)
        return queryset
