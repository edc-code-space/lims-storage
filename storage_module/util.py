from storage_module.models import BoxPosition


def get_available_positions(box):
    """
      This function retrieves available positions (x, y coordinates) within a given box.

      Args:
          box: A DimBox object representing the box to check for available positions.

      Returns:
          A list of tuples representing available (x, y) positions within the box.
      """
    occupied_positions = set(BoxPosition.objects.filter(box=box).
                             values_list('x_position', 'y_position'))
    max_position = box.box_capacity or 91
    all_positions = range(1, max_position + 1)
    free_positions = [(p, p) for p in all_positions if (p, p) not in occupied_positions]
    return free_positions


def get_data(input_list, url, icon, name, capacity, filter_obj):
    data_list = []
    for item in input_list:
        item_samples = filter_obj.filter(box=item).count()
        if item_samples > 0:
            data = {
                'id': item.id,
                'url': url,
                'icon': icon,
                'name': name,
                'capacity': capacity,
                'stored_samples': item_samples,
            }
            data_list.append(data)
    return data_list


def get_stored_samples(box):
    samples_in_box = BoxPosition.objects.filter(box=box).count()
    return samples_in_box


def get_data_dict(id, url, icon, name, capacity, stored_samples):
    return {
        'id': id,
        'url': url,
        'icon': icon,
        'name': name,
        'capacity': capacity,
        'stored_samples': stored_samples
    }


def append_if_samples(box, data_list, url, icon, name):
    samples_in_box = get_stored_samples(box)
    if samples_in_box > 0:
        _box = get_data_dict(box.id, url, icon, name, box.box_capacity, samples_in_box)
        data_list.append(_box)


def append_entity_info(entities, data_list, url, icon, name_attr):
    for entity in entities:
        capacity = 0
        stored_samples = 0
        for box in entity.boxes.all():
            samples_in_box = get_stored_samples(box)
            if samples_in_box > 0:
                capacity += box.box_capacity
                stored_samples += samples_in_box
        if stored_samples > 0:
            entity_dict = get_data_dict(entity.id, url, icon, getattr(entity, name_attr),
                                        capacity, stored_samples)
            data_list.append(entity_dict)


