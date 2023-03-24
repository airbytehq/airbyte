import mergedeep
from deepdiff import DeepDiff

def are_values_equal(value_1, value_2):
    if isinstance(value_1, dict) and isinstance(value_2, dict):
        diff = DeepDiff(value_1, value_2, ignore_order=True)
        return len(diff) == 0
    else:
        return value_1 == value_2

def merge_values(old_value, new_value):
    if isinstance(old_value, dict) and isinstance(new_value, dict):
        merged = old_value.copy()
        mergedeep.merge(merged, new_value)
        return merged
    else:
        return new_value
