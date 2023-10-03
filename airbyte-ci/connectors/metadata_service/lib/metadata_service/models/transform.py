#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

from pydantic import BaseModel


def _apply_default_pydantic_kwargs(kwargs: dict) -> dict:
    """A helper function to apply default kwargs to pydantic models.

    Args:
        kwargs (dict): the kwargs to apply

    Returns:
        dict: the kwargs with defaults applied
    """
    default_kwargs = {
        "by_alias": True,  # Ensure that the original field name from the jsonschema is used in the event it begins with an underscore (e.g. ab_internal)
        "exclude_none": True,  # Exclude fields that are None
    }

    return {**default_kwargs, **kwargs}


def to_json_sanitized_dict(pydantic_model_obj: BaseModel, **kwargs) -> dict:
    """A helper function to convert a pydantic model to a sanitized dict.

    Without this pydantic dictionary may contain values that are not JSON serializable.

    Args:
        pydantic_model_obj (BaseModel): a pydantic model

    Returns:
        dict: a sanitized dictionary
    """

    return json.loads(to_json(pydantic_model_obj, **kwargs))


def to_json(pydantic_model_obj: BaseModel, **kwargs) -> str:
    """A helper function to convert a pydantic model to a json string.

    Without this pydantic dictionary may contain values that are not JSON serializable.

    Args:
        pydantic_model_obj (BaseModel): a pydantic model

    Returns:
        str: a json string
    """
    kwargs = _apply_default_pydantic_kwargs(kwargs)

    return pydantic_model_obj.json(**kwargs)


def to_dict(pydantic_model_obj: BaseModel, **kwargs) -> dict:
    """A helper function to convert a pydantic model to a dict.

    Without this pydantic dictionary may contain values that are not JSON serializable.

    Args:
        pydantic_model_obj (BaseModel): a pydantic model

    Returns:
        dict: a dict
    """
    kwargs = _apply_default_pydantic_kwargs(kwargs)

    return pydantic_model_obj.dict(**kwargs)
