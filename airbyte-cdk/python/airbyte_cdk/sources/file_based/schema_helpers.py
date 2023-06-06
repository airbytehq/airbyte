from copy import deepcopy
from typing import Any, Dict, Mapping


type_widths = {str: 0}


def merge_schemas(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a new dictionary that contains schema1 and schema2.

    Schemas are merged as follows
    - If a key is in one schema but not the other, add it to the base schema with its existing type.
    - If a key is in both schemas but with different types, use the wider type.
    - If the type is a list in both schemas, form the union of the two.
    - If the type is a list in one schema but a different type of element in the other schema, raise an exception.
    - If the type is an object in both schemas but the objects are different raise an exception.
    - If the type is an object in one schema but not in the other schema, raise an exception.

    In other words, we support merging
    - any atomic type with any other atomic type (choose the wider of the two)
    - list with list (union)
    and nothing else.
    """
    merged_schema = deepcopy(schema1)
    for k2, t2 in schema2.items():
        t1 = merged_schema.get(k2)
        if t1 is None:
            merged_schema[k2] = t2
        elif t1 == t2:
            continue
        else:
            merged_schema[k2] = _choose_wider_type(k1, t1, t2)

    return merged_schema


def _choose_wider_type(key, t1: Any, t2: Any) -> Any:
    # TODO: more testing
    if t1 is None or t2 is None:
        return t1 or t2
    elif t1 in ("list", "object"):
        assert (
            t2 == "list"
        ), f"Incompatible types while merging schema field '{key}': {t1} and {t2}"
        return list(set(t1) | set(t2))
    elif t1 == "object":
        assert (
            t2 == "object"
        ), f"Incompatible types while merging schema field '{key}': {t1} and {t2}"
        return "object"
    elif t1 in type_widths and t2 in type_widths:
        return max(t1, t2, key=lambda t: type_widths[t])
    else:
        raise NotImplementedError(
            f"Unrecognized type while merging schema field '{key}': {t1}, {t2}"
        )


def conforms_to_schema(record: Mapping[str, Any], schema: Mapping[str, Any]) -> bool:
    """
    Return true iff the record conforms to the supplied schema.

    The record conforms to the supplied schema iff:
    - All columns in the record are in the schema.
    - For every column in the record, that column's type is equal to or narrower than the same column's
      type in the schema.
    """
    ...


def type_mapping_to_jsonschema(type_mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Return the user input schema (type mapping), transformed to JSON Schema format.
    """
    ...
