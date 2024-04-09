from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic import TemplateView

from .forms import MoveBoxForm, MoveSampleForm
from .models import BoxPosition, DimBox, DimFacility, DimFreezer, DimRack, DimShelf
from .models import DimSample, DimSampleStatus, Note


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
            'box_position__box__rack__shelf__freezer__facility__facility_name',
            'source_file__source_file_name',
            'box_position__box__box_name',
            'time__time_sampled',
            'sample_status__name'
        )
        if query:
            queryset = queryset.filter(sample_id__icontains=query)
        return queryset


class SampleDetailView(DetailView):
    model = DimSample
    template_name = 'storage_module/sample_detail.html'

    def get_object(self, queryset=None):
        sample_id = self.kwargs.get('sample_id')
        return get_object_or_404(DimSample, sample_id=sample_id)

    def post(self, request, *args, **kwargs):
        form = MoveSampleForm(request.POST)
        if form.is_valid():
            sample = self.get_object()

            new_box = form.cleaned_data['box']
            new_x = form.cleaned_data['x_position']
            new_y = form.cleaned_data['y_position']

            sample.box_position.box = new_box
            sample.box_position.x_position = new_x
            sample.box_position.y_position = new_y
            sample.box_position.save()

        note_content = request.POST.get('note')
        if note_content:
            user = request.user if request.user.is_authenticated else User.objects.get(
                username='Guest')
            Note.objects.create(sample=self.get_object(), author=user, text=note_content)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        box = self.object.box_position.box
        rack = box.location.get('rack', None)
        shelf = box.location.get('shelf', None)
        freezer = box.location.get('freezer', None)
        facility = box.location.get('facility', None)

        move_sample_form = MoveSampleForm(
            initial={'box': box.id}
        )

        context.update(
            box=box,
            rack=rack,
            shelf=shelf,
            freezer=freezer,
            facility=facility,
            sample=self.object,
            move_sample_form=move_sample_form,
        )
        return context


class BoxDetailView(DetailView):
    model = DimBox
    template_name = 'storage_module/box_detail.html'

    def get_object(self, queryset=None):
        box_id = self.kwargs.get('box_id')
        return get_object_or_404(DimBox, id=box_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            box = self.get_object()
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        box = self.object
        positions = box.positions.order_by('x_position', 'y_position')

        location = getattr(box, 'location', None)

        rack = location.get('rack', None)
        shelf = location.get('shelf', None)
        freezer = location.get('freezer', None)
        facility = location.get('facility', None)
        initial = {}
        if freezer:
            initial.update(freezer=freezer.id)
        if shelf:
            initial.update(shelf=shelf.id)
        if rack:
            initial.update(rack=rack.id)

        move_box_form = MoveBoxForm(
            initial=initial
        )

        context.update(
            box=box,
            positions=positions,
            rack=rack,
            shelf=shelf,
            freezer=freezer,
            facility=facility,
            move_box_form=move_box_form
        )

        return context


class RackDetailView(DetailView):
    model = DimRack
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        rack_id = self.kwargs.get('rack_id')
        return get_object_or_404(DimRack, id=rack_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            rack = self.get_object()
            box = rack.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        rack = self.object
        boxes = rack.boxes.all()
        move_box_form = MoveBoxForm()

        facility = None
        if rack.freezer:
            facility = getattr(rack, 'freezer').facility
        elif rack.shelf:
            facility = getattr(rack, 'shelf').freezer.facility
        elif boxes:
            facility = boxes[0].facility

        box_n_shelves_n_racks_data = []
        for box in rack.boxes.all():
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

        context['inside_freezer'] = box_n_shelves_n_racks_data
        context['type'] = 'rack'
        context['name'] = rack.rack_name
        context['obj'] = rack
        context['facility'] = facility

        return context


class ShelfDetailView(DetailView):
    model = DimShelf
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        shelf_id = self.kwargs.get('shelf_id')
        return get_object_or_404(DimShelf, id=shelf_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            shelf = self.get_object()
            box = shelf.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shelf = self.object
        boxes = shelf.boxes.all()
        move_box_form = MoveBoxForm()

        box_n_shelves_n_racks_data = []
        for box in shelf.boxes.filter(rack=None):
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

        for rack in shelf.racks.all():
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

        context['inside_freezer'] = box_n_shelves_n_racks_data
        context['type'] = 'Shelf'
        context['name'] = shelf.shelf_name
        context['obj'] = shelf
        context['facility'] = shelf.freezer.facility

        return context


class FreezerDetailView(DetailView):
    model = DimFreezer
    template_name = 'storage_module/freezer_detail.html'

    def get_object(self, queryset=None):
        freezer_id = self.kwargs.get('freezer_id')
        return get_object_or_404(DimFreezer, id=freezer_id)

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            freezer = self.get_object()
            box = freezer.boxes.get(id=request.POST['box_id'])
            box.freezer = form.cleaned_data.get('freezer')
            box.shelf = form.cleaned_data.get('shelf')
            box.rack = form.cleaned_data.get('rack')
            box.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        freezer = self.object
        boxes = freezer.boxes.all()
        move_box_form = MoveBoxForm()

        freezer_data = {}
        total_samples = BoxPosition.objects.count()

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

        context['inside_freezer'] = box_n_shelves_n_racks_data
        context['type'] = 'Freezer'
        context['name'] = freezer.freezer_name
        context['obj'] = freezer
        context['facility'] = freezer.facility

        return context


class FacilityListView(ListView):
    model = DimFacility
    template_name = "storage_module/storage_view.html"
    context_object_name = "facility_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context[self.context_object_name] = self.get_facilities
        return context

    @property
    def get_facilities(self):
        facilities = self.get_queryset()

        data = []
        for facility in facilities:
            freezers = facility.dimfreezer_set.all()

            facility_capacity = 0
            utilized_storage = 0

            for freezer in freezers:
                boxes = freezer.boxes.all()

                freezer_capacity = sum(box.box_capacity for box in boxes)
                facility_capacity += freezer_capacity

                for box in boxes:
                    utilized_storage += len(box.get_samples())

            data.append({
                'id': facility.id,
                'facility_name': facility.facility_name,
                'facility_capacity': facility_capacity,
                'utilized_storage': utilized_storage,
                'available_capacity': facility_capacity - utilized_storage
            })
        return data


class FacilityDetailView(DetailView):
    model = DimFacility
    template_name = "storage_module/facility_detail.html"
    context_object_name = "facility"
    slug_field = "facility_name"
    slug_url_kwarg = "facility_name"

    def get_object(self, queryset=None):
        facility_id = self.kwargs.get('facility_id')
        return get_object_or_404(DimFacility, id=facility_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facility = self.object
        facility_data = []
        total_samples = BoxPosition.objects.count()

        for freezer in facility.dimfreezer_set.all():
            freezer_data = {'freezer': freezer}
            freezer_total_capacity = freezer.boxes.aggregate(Sum('box_capacity'))[
                'box_capacity__sum']
            selected_box_ids = freezer.boxes.all().values_list('id', flat=True)
            freezer_total_samples = BoxPosition.objects.filter(
                box__id__in=selected_box_ids).count()

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

            freezer_data.update(
                inside_freezer=box_n_shelves_n_racks_data,
                freezer_total_capacity=freezer_total_capacity,
                freezer_total_samples=freezer_total_samples
            )

            facility_data.append(freezer_data)

        context['facility_data'] = facility_data
        return context
