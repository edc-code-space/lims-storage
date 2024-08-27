import csv
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from storage_module.forms import MoveBoxForm
from storage_module.models import BoxPosition, DimBox, DimSample


class ViewMixin:
    """
    Export samples as CSV file.

    Parameters:
    - sample_ids (list): A list of sample IDs to be exported.

    Returns:
    - response (HttpResponse): The CSV file as a HTTP response.

    Example:
    ```
    view = ViewMixin()
    sample_ids = [1, 2, 3]
    response = view.export_samples_as_csv(sample_ids)
    ```
    """

    def export_samples_as_csv(self, sample_ids):
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=samples_{timestamp_str}.csv'

        writer = csv.writer(response)
        headers = ['Sample ID', 'Sample Type', 'Source File Name', 'Condition',
                   'Created By', 'Participant ID', 'Gender', 'Date of Birth',
                   'Date Sampled', 'Time Sampled', 'Requisition ID', 'Protocol Number',
                   'Facility Name', 'Box Name', 'Sample Status']
        writer.writerow(headers)

        samples = DimSample.objects.filter(sample_id__in=sample_ids)
        for sample in samples:
            writer.writerow([
                sample.sample_id,
                sample.sample_type.sample_type if sample.sample_type else "",
                sample.source_file.source_file_name if sample.source_file else "",
                sample.sample_condition if sample.sample_condition else "",
                sample.user_created if sample.user_created else "",
                sample.participant_id if sample.participant_id else "",
                sample.gender if sample.gender else "",
                sample.date_of_birth if sample.date_of_birth else "",
                sample.date_sampled if sample.date_sampled else "",
                sample.time_sampled if sample.time_sampled else "",
                sample.requisition_id if sample.requisition_id else "",
                sample.protocol_number if sample.protocol_number else "",
                sample.facility.facility_name if sample.facility else "",
                sample.box.box_name if sample.box else "",
                sample.sample_status.name if sample.sample_status else ""
            ])

        return response


class BaseStorageDetailView(LoginRequiredMixin, DetailView):
    """
    This is the documentation for the given code:

    class BaseStorageDetailView(LoginRequiredMixin, DetailView):
        This is a class that represents a base storage detail view. It is a subclass of
        LoginRequiredMixin and DetailView.

        get_object(self, queryset=None):
            This function returns the object with the given id from the model specified
            in the class. If no object is found with the given id, a 404 error is raised.

        post(self, request, *args, **kwargs):
            This function is called when a POST request is made to the view. It
            initializes a MoveBoxForm with the POST data. If the form is valid,
            it calls the process_form method and then calls the get method of the
            superclass with the given arguments. It returns the result of the
            superclass method.

        process_form(self, request, form):
            This function processes the form data and updates the relevant fields of a
            box object. It takes a request object and a form object as parameters.

        get_context_data(self, **kwargs):
            This function returns the context data for the view. It calls the
            get_context_data method of the superclass and then updates the context data
            with additional information related to the storage. It returns the updated
            context data.

        build_display_data(self):
            This function builds and returns the display data for the view. It calls
            the get_containers method to get a list of containers and then calls the
            get_container_data method for each container to get the container data. It
            returns the container data.

        get_containers(self):
            This is a placeholder method that should be implemented by subclasses. It
            should return a list of containers.

        get_container_data(self, container_type, queryset_objs, icon):
            This function returns the container data for a given container type,
            queryset of objects, and icon. It iterates over the queryset of objects and
            retrieves the relevant data for each object. It returns a list of container
            data.

        get_facility(self, storage):
            This function returns the facility associated with the given storage
            object. If the storage object has a freezer attribute, it returns the
            facility of the freezer. If the storage object has a shelf attribute,
            it returns the facility of the shelf's freezer. If neither of these
            conditions is true, it returns None.
    """

    form_class = MoveBoxForm

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs.get(self.lookup_id))

    def post(self, request, *args, **kwargs):
        form = MoveBoxForm(request.POST)
        if form.is_valid():
            self.process_form(request, form)
        return super().get(request, *args, **kwargs)

    def process_form(self, request, form):
        storage = self.get_object()
        box = storage.boxes.get(id=request.POST['box_id'])
        box.freezer = form.cleaned_data.get('freezer')
        box.shelf = form.cleaned_data.get('shelf')
        box.rack = form.cleaned_data.get('rack')
        box.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inside_freezer'] = self.build_display_data()
        total_samples = sum(item['stored_samples'] for item in context['inside_freezer'])
        total_capacity = sum(item['capacity'] for item in context['inside_freezer'])
        storage = self.object
        context.update({
            "total_samples": total_samples,
            "total_capacity": total_capacity,
            "percent_filled": (total_samples / total_capacity) * 100 if total_capacity
            else 0,
            'type': self.storage_type,
            'name': getattr(self.object, f"{self.storage_type}_name"),
            'obj': self.object,
            'icon': self.storage_icon,
            'facility': self.get_facility(storage)
        })
        return context

    def build_display_data(self):
        """
        Builds display data for the object's containers.

        :return: A list of container data, containing container types, icons,
        and querysets.
        """
        container_data = []
        for container in self.get_containers():
            container_type = container['type']
            icon = container['icon']
            queryset = container['queryset']
            container_data.extend(self.get_container_data(container_type, queryset, icon))
        return container_data

    def get_containers(self):
        raise NotImplementedError("Subclasses should implement this method")

    def get_container_data(self, container_type, queryset_objs, icon):
        """
        This method `get_container_data` returns a list of container data based on the
        given parameters.

        :param container_type: The type of container to get data for.
        :param queryset_objs: A queryset of container objects to generate data from.
        :param icon: The icon to associate with each container.

        :return: A list of dictionaries, each representing container data. Each
        dictionary contains the following keys:
                 - 'id': The ID of the container.
                 - 'url': The URL to access the container's detail page.
                 - 'icon': The icon associated with the container.
                 - 'name': The name of the container.
                 - 'capacity': The total capacity of the container.
                 - 'stored_samples': The number of samples stored in the container.

        Example usage:
            container_data = get_container_data("box", Box.objects.all(), "box-icon")

            Output:
            [
                {'id': 1, 'url': 'box_detail', 'icon': 'box-icon', 'name': 'Box 1',
                'capacity': 10, 'stored_samples': 5},
                {'id': 2, 'url': 'box_detail', 'icon': 'box-icon', 'name': 'Box 2',
                'capacity': 15, 'stored_samples': 0},
                ...
            ]
        """
        container_data = []
        for container in queryset_objs:
            if isinstance(container, DimBox):
                capacity = container.box_capacity
                samples_attr = {'box': container}
            else:
                capacity = container.boxes.aggregate(total_capacity=Sum('box_capacity'))[
                    'total_capacity']
                samples_attr = {'box__{}__id'.format(container_type): container.id}

            samples = BoxPosition.objects.filter(**samples_attr).count()
            if samples > 0:
                container_data.append({
                    'id': container.id,
                    'url': f'{container_type}_detail',
                    'icon': icon,
                    'name': getattr(container, f"{container_type}_name"),
                    'capacity': capacity,
                    'stored_samples': samples
                })
        return container_data

    def get_facility(self, storage):
        """
        Retrieve the facility information of a given storage.

        :param storage: The storage object from which to retrieve the facility information.
        :return: The facility information of the storage, or None if it cannot be determined.
        """
        if hasattr(storage, 'freezer') and storage.freezer:
            return storage.freezer.facility
        elif hasattr(storage, 'shelf') and storage.shelf:
            return storage.shelf.freezer.facility
        elif hasattr(storage, 'facility'):
            return storage.facility

        return None
