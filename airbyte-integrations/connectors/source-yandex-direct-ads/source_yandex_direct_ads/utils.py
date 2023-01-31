def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def find_by_key(data, target):
    """Search for target values in nested dict"""
    for key, value in data.items():
        if isinstance(value, dict):
            yield from find_by_key(value, target)
        elif key == target:
            yield value


def concat_multiple_lists(list_of_lists):
    return sum(list_of_lists, [])


def get_unique(list1):
    return list(set(list1))
