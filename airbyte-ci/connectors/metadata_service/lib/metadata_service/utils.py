import json
from pydantic import BaseModel


def to_json_sanitized_dict(pydantic_model_obj: BaseModel, **kwargs) -> dict:
    """A helper function to convert a pydantic model to a sanitized dict.

    Without this pydantic dictionary may contain values that are not JSON serializable.

    Args:
        pydantic_model_obj (BaseModel): a pydantic model

    Returns:
        dict: a sanitized dictionary
    """
    defalut_kwargs = {
        "by_alias": True, # Ensure that the original field name from the jsonschema is used in the event it begins with an underscore (e.g. _ab_internal)
    }

    kwargs = {**defalut_kwargs, **kwargs}

    return json.loads(pydantic_model_obj.json(**kwargs))
