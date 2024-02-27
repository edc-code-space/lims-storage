import os

import django
from faker import Faker

from storage_module.models import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storage_module.settings")

django.setup()

fake_gen = Faker()

facilities = [DimFacility.objects.create(facility_name=fake_gen.company()) for _ in
              range(100)]
sample_types = [DimSampleType.objects.create(sample_type=fake_gen.job()) for _ in
                range(100)]
files = [DimSourceFile.objects.create(source_file_name=f'Sample File{i}',
                                      source_file_description=fake_gen.text()) for i in
         range(100)]
boxes = [
    DimBox.objects.create(box_name=fake_gen.word(), box_description=fake_gen.sentence())
    for _ in range(100)]
times = [DimTime.objects.create(time_sampled=fake_gen.time(),
                                time_of_day=fake_gen.day_of_month(),
                                day_of_week=fake_gen.day_of_week()) for _ in range(100)]

for i in range(100):
    DimSample.objects.create(
        sample_id=f'Sample{i}',
        sample_type=sample_types[i],
        facility=facilities[i],
        source_file=files[i],
        box=boxes[i],
        time=times[i],
    )

print("Data creation done!")
