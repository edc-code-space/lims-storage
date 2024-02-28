from django.apps import AppConfig as DjangoAppConfig
from edc_base.apps import AppConfig as BaseEdcBaseAppConfig


class AppConfig(DjangoAppConfig):
    name = 'storage_module'


class EdcBaseAppConfig(BaseEdcBaseAppConfig):
    project_name = 'storage_module'
    institution = 'Botswana-Harvard AIDS Institute'
