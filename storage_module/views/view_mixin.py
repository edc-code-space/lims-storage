import csv
from datetime import datetime

from django.http import HttpResponse

from storage_module.models import DimSample


class ViewMixin:

    def export_samples_as_csv(self, sample_ids):
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=samples_{timestamp_str}.csv'

        writer = csv.writer(response)
        headers = ['Sample ID', 'Sample Type', 'Facility Name', 'Source File Name',
                   'Box Name', 'Time Sampled', 'Sample Status']
        writer.writerow(headers)

        samples = DimSample.objects.filter(sample_id__in=sample_ids)
        for sample in samples:
            writer.writerow([
                sample.sample_id,
                sample.sample_type.sample_type if sample.sample_type else "",
                sample.facility.facility_name if sample.facility else "",
                sample.source_file.source_file_name if sample.source_file else "",
                sample.box.box_name if sample.box else "",
                sample.date_sampled,
                sample.sample_status.name if sample.sample_status else ""
            ])

        return response
