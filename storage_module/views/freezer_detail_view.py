from .view_mixin import BaseStorageDetailView
from ..models import (DimFreezer)


class FreezerDetailView(BaseStorageDetailView):
    model = DimFreezer
    template_name = 'storage_module/freezer_detail.html'
    lookup_id = 'freezer_id'
    storage_type = 'freezer'
    storage_icon = 'fas fa-snowflake'

    def get_containers(self):
        freezer = self.object
        return [
            {'type': 'box', 'queryset': freezer.boxes.filter(shelf=None, rack=None),
             'icon': 'fas fa-cube'},
            {'type': 'shelf', 'queryset': freezer.shelves.all(),
             'icon': 'fas fa-layer-group'},
            {'type': 'rack', 'queryset': freezer.racks.all(), 'icon': 'fas fa-box-open'}
        ]

