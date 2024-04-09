from django import template

from django.apps import apps as django_apps

register = template.Library()


@register.filter
def make_range(n):
    return range(n)


@register.simple_tag
def is_instance(obj, model_name):
    model = django_apps.get_model(app_label='storage_module', model_name=model_name)
    return isinstance(obj, model)
