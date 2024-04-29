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
