from storage_module.models import DimRack
from storage_module.views.view_mixin import BaseStorageDetailView


class RackDetailView(BaseStorageDetailView):
    model = DimRack
    template_name = 'storage_module/freezer_detail.html'
    lookup_id = 'rack_id'
    storage_type = 'rack'
    storage_icon = 'fas fa-box-open'

    def get_containers(self):
        rack = self.object
        return [{'type': 'box', 'queryset': rack.boxes.all(), 'icon': 'fas fa-cube'}]
