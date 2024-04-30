from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from storage_module.forms import MoveSampleForm
from storage_module.models import BoxPosition, DimBox, DimSample, Note


class SampleDetailView(LoginRequiredMixin, DetailView):
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
            sample_box_position = self.sample_position
            sample_box_position.box = form.cleaned_data['box']
            sample_box_position.x_position = form.cleaned_data['x_position']
            sample_box_position.y_position = form.cleaned_data['y_position']
            sample_box_position.save()

        note_content = request.POST.get('note')
        if note_content:
            user = request.user if request.user.is_authenticated else User.objects.get(
                username='Guest')
            Note.objects.create(sample=self.get_object(), author=user, text=note_content)
        return super().get(request, *args, **kwargs)

    def get_location(self, loc):
        return self.box.location.get(loc, None) if self.box else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {'box': self.box.id} if self.box else {}
        move_sample_form = MoveSampleForm(
            initial=initial
        )

        context.update(
            box=self.box,
            rack=self.get_location('rack'),
            shelf=self.get_location('shelf'),
            freezer=self.get_location('freezer'),
            facility=self.get_location('facility'),
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
