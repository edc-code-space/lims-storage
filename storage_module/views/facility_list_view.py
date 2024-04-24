from django.views.generic import ListView

from ..models import DimFacility


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
