"""
This script is responsible for connectors spec.json file validation.

Input:
List of spec files

Output:
exit code 0 - check is success
exit code 1 - check failed for at least one spec file

How spec file validation works:
1. read spec file and serialize it as python dict object
2. get properties field from spec object
3. check if all fields from FIELDS_TO_CHECK exist in each property
4. if field has oneOf attribute - fetch all subobjects and for each of them goto step (2)
"""

import logging
import sys
import json
from collections import defaultdict
from typing import Any, List, Mapping

# errors counter
ERRORS = defaultdict(int)
# required fields for each property field in spec
FIELDS_TO_CHECK = {"title", "description"}
# configure logging
logging.basicConfig(format="%(message)s")


def read_spec_file(spec_path: str):
    with open(spec_path) as json_file:
        try:
            root_schema = json.load(json_file)["connectionSpecification"]["properties"]
        except KeyError:
            logging.error(f"\033[1m{spec_path}\033[0m: Couldn't find properties in connector spec.json")
            ERRORS[spec_path] += 1
            return

    validate_schema(spec_path, root_schema)


def validate_schema(
    spec_path: str,
    schema: Mapping[str, Any],
    parent_fields: List[str] = None,
):
    parent_fields = parent_fields if parent_fields else []
    for field_name, field_schema in schema.items():
        if not FIELDS_TO_CHECK.issubset(field_schema):
            full_field_name = get_full_field_name(field_name, parent_fields)
            logging.error(f"\033[1m{spec_path}\033[0m: Check failed for field \x1b[31;1m{full_field_name}\033[0m")
            ERRORS[spec_path] += 1

        for index, oneof_schema in enumerate(fetch_oneof_schemas(field_schema)):
            validate_schema(spec_path, oneof_schema["properties"], parent_fields + [field_name, str(index)])


def fetch_oneof_schemas(schema: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """
    Finds sub-objects in oneOf field
    """
    if schema.get("oneOf") and schema["type"] == "object":
        return [spec for spec in schema["oneOf"] if spec.get("properties")]
    return []


def get_full_field_name(field_name: str, parent_fields: List[str] = None):
    """
    Returns full path to a field.
    e.g. root.middle.child, root.oneof.1.attr
    """
    return ".".join(parent_fields + [field_name]) if parent_fields else field_name


if __name__ == "__main__":
    spec_files = sys.argv[1:]

    for file_path in spec_files:
        read_spec_file(file_path)

    if ERRORS:
        exit(1)
