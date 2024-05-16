from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from ..models import DimBox, DimFacility


class FacilityListView(LoginRequiredMixin, ListView):
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

            boxes_list = []

            samples = 0

            for freezer in freezers:
                boxes = DimBox.objects.filter(
                    Q(shelf__freezer=freezer) |
                    Q(rack__shelf__freezer=freezer) |
                    Q(rack__freezer=freezer) |
                    Q(freezer=freezer)
                )

                freezer_capacity = sum(box.box_capacity for box in boxes)
                facility_capacity += freezer_capacity

                boxes_list += list(boxes)

                for box in boxes:
                    samples += len(box.get_samples())

            utilized_storage = round(((samples / facility_capacity)
                                      * 100), 1) if facility_capacity else 0

            data.append({
                'id': facility.id,
                'facility_name': facility.facility_name,
                'samples': samples,
                'boxes': len(boxes_list),
                'facility_capacity': facility_capacity,
                'utilized_storage': utilized_storage,
                'available_capacity': facility_capacity - utilized_storage
            })
        return data
