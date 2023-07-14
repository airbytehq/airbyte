import mergedeep
import json
from deepdiff import DeepDiff
from typing import TypeVar
from pydantic import BaseModel
import copy

T = TypeVar("T")


def are_values_equal(value_1: any, value_2: any) -> bool:
    if isinstance(value_1, dict) and isinstance(value_2, dict):
        diff = DeepDiff(value_1, value_2, ignore_order=True)
        return len(diff) == 0
    else:
        return value_1 == value_2


def merge_values(old_value: T, new_value: T) -> T:
    if isinstance(old_value, dict) and isinstance(new_value, dict):
        merged = old_value.copy()
        mergedeep.merge(merged, new_value)
        return merged
    else:
        return new_value


def deep_copy_params(to_call):
    def f(*args, **kwargs):
        return to_call(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    return f


def to_json_sanitized_dict(pydantic_model_obj: BaseModel) -> dict:
    """A helper function to convert a pydantic model to a sanitized dict.

    Without this pydantic dictionary may contain values that are not JSON serializable.

    Args:
        pydantic_model_obj (BaseModel): a pydantic model

    Returns:
        dict: a sanitized dictionary
    """
    return json.loads(pydantic_model_obj.json())
