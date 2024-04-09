import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storage_module.settings")

django.setup()

import random
from faker import Faker
from django.contrib.auth.models import User
from storage_module.models import (DimFacility, DimSampleType, DimSourceFile, BoxPosition,
                                   DimBox,
                                   DimTime, DimSampleStatus, Note, DimSample, DimRack,
                                   DimShelf, DimFreezer)

fake = Faker()

# Generate users
for _ in range(5):
    User.objects.create_user(username=fake.user_name(), email=fake.email(),
                             password=fake.password())

# Generate facilities
facilities = []
for _ in range(5):
    facility, created = DimFacility.objects.get_or_create(
        facility_name=fake.company()
    )
    facilities.append(facility)

# Generate sample types
sample_types = []
for _ in range(10):
    sample_type, created = DimSampleType.objects.get_or_create(
        sample_type=fake.word(ext_word_list=None)
    )
    sample_types.append(sample_type)

# Generate source files
source_files = []
for _ in range(10):
    source_file, created = DimSourceFile.objects.get_or_create(
        source_file_name=fake.file_name(category=None, extension="txt"),
        source_file_description=fake.text(max_nb_chars=100)
    )
    source_files.append(source_file)


def create_box(rack=None, shelf=None, freezer=None):
    return DimBox.objects.get_or_create(
        box_name=f"box{x + 1}",
        box_description=fake.text(max_nb_chars=100),
        box_capacity=100,
        rack=rack,
        shelf=shelf,
        freezer=freezer
    )


# Generate freezers, shelves, racks, boxes for each facility
# Removed code for brevity ...

# Generate freezers, shelves, racks, boxes for each facility
for facility in facilities:
    for i in range(5):
        boxes = []

        freezer, _ = DimFreezer.objects.get_or_create(
            freezer_name=f"freezer{i + 1}",
            freezer_description=fake.text(max_nb_chars=100),
            facility=facility
        )

        for x in range(10):
            box, _ = create_box(freezer=freezer)
            boxes.append(box)

        shelf, _ = DimShelf.objects.get_or_create(
            shelf_name=f"shelf{i + 1}",
            shelf_description=fake.text(max_nb_chars=100),
            freezer=freezer
        )

        for x in range(10):
            box, _ = create_box(shelf=shelf, freezer=freezer)
            boxes.append(box)

        rack, _ = DimRack.objects.get_or_create(
            rack_name=f"rack{i + 1}",
            rack_description=fake.text(max_nb_chars=100),
            shelf=shelf,
        )

        for x in range(10):
            box, _ = create_box(rack=rack, shelf=shelf, freezer=freezer)
            boxes.append(box)

        # Generate samples and place them to random box
        for box in boxes:
            x_position = 0
            y_position = 0
            for _ in range(10):  # reduced to 10 to fit in a 10*10 box
                time, _ = DimTime.objects.get_or_create(
                    time_sampled=fake.time(pattern="%H:%M:%S", end_datetime=None),
                    time_of_day=fake.time(pattern="%H:%M", end_datetime=None),
                    day_of_week=fake.day_of_week()
                )

                sample_status, _ = DimSampleStatus.objects.get_or_create(
                    name=fake.word(ext_word_list=None),
                    description=fake.text(max_nb_chars=100)
                )

                sample, _ = DimSample.objects.get_or_create(
                    sample_id=fake.unique.random_number(digits=5),
                    sample_type=random.choice(sample_types),
                    source_file=random.choice(source_files),
                    time=time,
                    sample_status=sample_status
                )

                box_position = BoxPosition.objects.create(
                    sample=sample,
                    box=box,
                    x_position=x_position,
                    y_position=y_position
                )

                # Add some notes to sample
                note = Note.objects.create(
                    sample=sample,
                    author=random.choice(User.objects.all()),
                    text=fake.text(max_nb_chars=100),
                    created_date=fake.date_time_this_year(before_now=True,
                                                          after_now=False,
                                                          tzinfo=None)
                )

                # update x_position and y_position for next sample in the current box
                x_position += 1
                if x_position > 9:
                    x_position = 0
                    y_position += 1
