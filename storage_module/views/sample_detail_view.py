from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from storage_module.forms import MoveSampleForm
from storage_module.models import BoxPosition, DimBox, DimSample, Note


class SampleDetailView(DetailView):
    model = DimSample
    template_name = 'storage_module/sample_detail.html'

    x_labels = [int(i) for i in range(1, 10)]
    y_labels = [chr(i) for i in range(ord('A'), ord('J'))]

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

        rack = self.box.location.get('rack', None) if self.box else None
        shelf = self.box.location.get('shelf', None) if self.box else None
        freezer = self.box.location.get('freezer', None) if self.box else None
        facility = self.box.location.get('facility', None) if self.box else None
        initial = {'box': self.box.id} if self.box else {}
        move_sample_form = MoveSampleForm(
            initial=initial
        )

        context.update(
            box=self.box,
            rack=rack,
            shelf=shelf,
            freezer=freezer,
            facility=facility,
            sample=self.object,
            move_sample_form=move_sample_form,
            x_labels=self.x_labels,
            y_labels=self.y_labels,
            sample_position=self.sample_position
        )
        return context

    @property
    def sample_position(self):
        try:
            sample_position = BoxPosition.objects.get(sample_id=self.object.sample_id)
        except BoxPosition.DoesNotExist:
            sample_position = None
        return sample_position

    @property
    def box(self):
        box = None
        if self.sample_position:
            try:
                box = DimBox.objects.get(boxposition=self.sample_position)
            except DimBox.DoesNotExist:
                box = None
        return box
