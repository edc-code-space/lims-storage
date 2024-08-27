from .view_mixin import BaseStorageDetailView
from ..models import (DimShelf)


class ShelfDetailView(BaseStorageDetailView):
    model = DimShelf
    template_name = 'storage_module/freezer_detail.html'
    lookup_id = 'shelf_id'
    storage_type = 'shelf'
    storage_icon = 'fas fa-layer-group'

    def get_containers(self):
        shelf = self.object
        return [
            {'type': 'box', 'queryset': shelf.boxes.filter(rack=None),
             'icon': 'fas fa-cube'},
            {'type': 'rack', 'queryset': shelf.racks.all(), 'icon': 'fas fa-box-open'}
        ]
