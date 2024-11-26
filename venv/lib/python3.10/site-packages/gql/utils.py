"""Utilities to manipulate several python objects."""

from typing import Any, Dict, List, Tuple, Type


# From this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() if x else "_" for x in components[1:])


def extract_files(
    variables: Dict, file_classes: Tuple[Type[Any], ...]
) -> Tuple[Dict, Dict]:
    files = {}

    def recurse_extract(path, obj):
        """
        recursively traverse obj, doing a deepcopy, but
        replacing any file-like objects with nulls and
        shunting the originals off to the side.
        """
        nonlocal files
        if isinstance(obj, list):
            nulled_obj = []
            for key, value in enumerate(obj):
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj.append(value)
            return nulled_obj
        elif isinstance(obj, dict):
            nulled_obj = {}
            for key, value in obj.items():
                value = recurse_extract(f"{path}.{key}", value)
                nulled_obj[key] = value
            return nulled_obj
        elif isinstance(obj, file_classes):
            # extract obj from its parent and put it into files instead.
            files[path] = obj
            return None
        else:
            # base case: pass through unchanged
            return obj

    nulled_variables = recurse_extract("variables", variables)

    return nulled_variables, files


def str_first_element(errors: List) -> str:
    try:
        first_error = errors[0]
    except (KeyError, TypeError):
        first_error = errors

    return str(first_error)
