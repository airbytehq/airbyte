from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from pydantic import BaseModel


def get(obj: dict[str, Any] | BaseModel, key_path: str, default: Any = None) -> Any:
    """Get the value of an arbitrarily nested key in a dictionary or Pydantic model instance

    Args:
        obj (Any): The object from which the value is to be extracted.
        key_path (str): A dotted path to the key to be extracted.
        default (Any, optional): The fallback value if the given key does not exist. Defaults to None.

    Returns:
        Any: The value found at the specified key path.
    """
    obj = obj if isinstance(obj, dict) else obj.json()

    current = obj
    keys = key_path.split(".")

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current
