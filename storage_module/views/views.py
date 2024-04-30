from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from storage_module.models import (BoxPosition, DimFreezer, DimRack,
                                   DimShelf)


class HomeView(TemplateView):
    template_name = 'storage_module/home.html'


def get_shelves(request):
    freezer_id = request.GET.get('freezer_id')
    shelves = DimShelf.objects.filter(freezer_id=freezer_id).values()
    return JsonResponse(list(shelves), safe=False)


def get_racks(request):
    freezer = request.GET.get('freezer_id')
    racks = DimRack.objects.filter(freezer_id=freezer).values()
    return JsonResponse(list(racks), safe=False)


def freezer_data(request, freezer_id):
    freezer = get_object_or_404(DimFreezer, id=freezer_id)
    box_n_shelves_n_racks_data = []
    for box in freezer.boxes.filter(shelf=None, rack=None):
        samples_in_box = BoxPosition.objects.filter(box=box).count()
        if samples_in_box > 0:
            _box = {
                'id': box.id,
                'url': 'box_detail',
                'icon': 'fas fa-cube',
                'name': box.box_name,
                'capacity': box.box_capacity,
                'stored_samples': samples_in_box,
            }
            box_n_shelves_n_racks_data.append(_box)

    for shelf in freezer.shelves.all():
        boxes_on_shelf = shelf.boxes.all()
        capacity = 0
        boxes_on_shelf_samples = 0
        for box in boxes_on_shelf:
            boxes_on_shelf_samples = BoxPosition.objects.filter(box=box).count()
            if boxes_on_shelf_samples > 0:
                capacity += box.box_capacity
        _shelf = {
            'id': shelf.id,
            'url': 'shelf_detail',
            'icon': 'fas fa-layer-group',
            'name': shelf.shelf_name,
            'capacity': capacity,
            'stored_samples': boxes_on_shelf_samples
        }
        box_n_shelves_n_racks_data.append(_shelf)

    for rack in freezer.racks.all():
        boxes_on_rack = rack.boxes.all()
        capacity = 0
        boxes_on_rack_samples = 0
        for box in boxes_on_rack:
            boxes_on_rack_samples = BoxPosition.objects.filter(box=box).count()
            if boxes_on_rack_samples > 0:
                capacity += box.box_capacity
        _rack = {
            'id': rack.id,
            'url': 'rack_detail',
            'icon': 'fas fa-box-open',
            'name': rack.rack_name,
            'capacity': capacity,
            'stored_samples': boxes_on_rack_samples
        }
        box_n_shelves_n_racks_data.append(_rack)
    html = render_to_string("storage_module/child_box_detail.html",
                            {'inside_freezer': box_n_shelves_n_racks_data})
    return JsonResponse({'html': html})
