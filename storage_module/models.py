from django.db import models
from simple_history.models import HistoricalRecords

class DimFacility(models.Model):
    facility_name = models.CharField(max_length=255)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimfacility'


class DimSampleType(models.Model):
    sample_type = models.CharField(max_length=255)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimsampletype'


class DimSourceFile(models.Model):
    source_file_name = models.CharField(max_length=100)
    source_file_description = models.TextField()

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimsourcefile'


class DimBox(models.Model):
    box_name = models.CharField(max_length=255)
    box_description = models.TextField()

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimbox'


class DimTime(models.Model):
    time_sampled = models.CharField(max_length=10)
    time_of_day = models.CharField(max_length=50)
    day_of_week = models.CharField(max_length=20)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimtime'


class DimSampleStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimsamplestatus'


class DimSample(models.Model):
    sample_id = models.CharField(max_length=255)
    sample_type = models.ForeignKey('DimSampleType', on_delete=models.CASCADE)
    facility = models.ForeignKey('DimFacility', on_delete=models.CASCADE)
    source_file = models.ForeignKey('DimSourceFile', on_delete=models.CASCADE)
    box = models.ForeignKey('DimBox', on_delete=models.CASCADE)
    time = models.ForeignKey('DimTime', on_delete=models.CASCADE)
    sample_status = models.ForeignKey('DimSampleStatus', on_delete=models.CASCADE,
                                      null=True)

    history = HistoricalRecords()

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimsample'


class DimRack(models.Model):
    rack_name = models.CharField(max_length=50)
    rack_description = models.TextField()
    sample = models.ForeignKey('DimSample', on_delete=models.CASCADE)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimrack'


# Note: Before creating 'DimLocation', you need to make sure that 'DimFreezer',
# 'DimFacility', 'DimShelf' and 'DimRack' tables exist

class DimShelf(models.Model):
    shelf_name = models.CharField(max_length=50)
    shelf_description = models.TextField()
    rack = models.ForeignKey('DimRack', on_delete=models.CASCADE)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimshelf'


class DimFreezer(models.Model):
    freezer_name = models.CharField(max_length=255)
    freezer_description = models.TextField()
    shelf = models.ForeignKey('DimShelf', on_delete=models.CASCADE)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimfreezer'


class DimLocation(models.Model):
    freezer = models.ForeignKey('DimFreezer', on_delete=models.CASCADE)
    facility = models.ForeignKey('DimFacility', on_delete=models.CASCADE)
    shelf = models.ForeignKey('DimShelf', on_delete=models.CASCADE)
    rack = models.ForeignKey('DimRack', on_delete=models.CASCADE)

    class Meta:
        app_label = 'storage_module'
        db_table = 'dimlocation'


class MeasureSampleCountsByFacility(models.Model):
    facility = models.ForeignKey('DimFacility', on_delete=models.CASCADE)
    sample_count = models.IntegerField()

    class Meta:
        app_label = 'storage_module'
        db_table = 'measuresamplecounts'


class MeasureSampleTypeCountsByFacility(models.Model):
    facility = models.ForeignKey('DimFacility', on_delete=models.CASCADE)
    sample_type = models.ForeignKey('DimSampleType', on_delete=models.CASCADE)
    sample_type_count = models.IntegerField()

    class Meta:
        app_label = 'storage_module'
        db_table = 'measuresampletypecounts'
