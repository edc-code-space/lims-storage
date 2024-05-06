from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from storage_module.models import (BoxPosition, DimFreezer, DimRack,
                                   DimSample, DimSampleType, DimShelf)
from storage_module.util import get_data


class HomeView(TemplateView):
    template_name = 'storage_module/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_specimen'] = DimSample.objects.all().count()
        context['specimen_types'] = DimSampleType.objects.all().count()
        context['unique_participants'] = DimSample.objects.values(
            'participant_id').distinct().count()
        context['studies'] = DimSample.objects.values(
            'protocol_number').distinct().count()

        return context


@login_required
def get_shelves(request):
    freezer_id = request.GET.get('freezer_id')
    shelves = DimShelf.objects.filter(freezer_id=freezer_id).values()
    return JsonResponse(list(shelves), safe=False)


@login_required
def get_racks(request):
    freezer = request.GET.get('freezer_id')
    racks = DimRack.objects.filter(freezer_id=freezer).values()
    return JsonResponse(list(racks), safe=False)


@login_required
def freezer_data(request, freezer_id):
    freezer = get_object_or_404(DimFreezer, id=freezer_id)
    box_n_shelves_n_racks_data = []

    box_n_shelves_n_racks_data += get_data(freezer.boxes.filter(shelf=None, rack=None),
                                           'box_detail', 'fas fa-cube',
                                           lambda box: box.box_name,
                                           lambda box: box.box_capacity,
                                           BoxPosition.objects)
    box_n_shelves_n_racks_data += get_data(freezer.shelves.all(), 'shelf_detail',
                                           'fas fa-layer-group',
                                           lambda shelf: shelf.shelf_name,
                                           sum([box.box_capacity for box in
                                                shelf.boxes.all() if
                                                BoxPosition.objects.filter(
                                                    box=box).count() > 0]),
                                           BoxPosition.objects)
    box_n_shelves_n_racks_data += get_data(freezer.racks.all(), 'rack_detail',
                                           'fas fa-box-open', lambda rack: rack.rack_name,
                                           sum([box.box_capacity for box in
                                                rack.boxes.all() if
                                                BoxPosition.objects.filter(
                                                    box=box).count() > 0]),
                                           BoxPosition.objects)

    html = render_to_string("storage_module/child_box_detail.html",
                            {'inside_freezer': box_n_shelves_n_racks_data})
    return JsonResponse({'html': html})
