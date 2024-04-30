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