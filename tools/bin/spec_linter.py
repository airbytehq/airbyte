import logging
import sys
import os
import json
from collections import defaultdict
from typing import Any, List, Mapping, Union

# errors counter
ERRORS = defaultdict(int)
# required fields for each property field in spec
FIELDS_TO_CHECK = {"title", "description"}
# configure logging
logging.basicConfig(format="%(message)s")


def parse_spec(spec_path: str):
    with open(spec_path) as json_file:
        try:
            properties = json.load(json_file)['connectionSpecification']['properties']
        except KeyError:
            logging.error(f"\033[1m{spec_path}\033[0m: Couldn't find properties in connector spec.json")
            ERRORS[spec_path] += 1
            return

    return validate_spec_field(spec_path, properties)


def validate_spec_field(
    spec_path: str,
    spec_object: Union[Mapping[str, Any], List],
    parent_fields: List[str] = None
):
    parent_fields = parent_fields if parent_fields else []
    if isinstance(spec_object, dict):
        for field_name, field_object in spec_object.items():
            if not FIELDS_TO_CHECK.issubset(field_object):
                full_field_name = get_full_field_name(field_name, parent_fields)
                logging.error(f"\033[1m{spec_path}\033[0m: Check failed for field \x1b[31;1m{full_field_name}\033[0m")
                ERRORS[spec_path] += 1
                validate_spec_field()
    elif isinstance(spec_object, list)


def get_full_field_name(field_name: str, parent_fields: List[str] = None):
    return '.'.join(parent_fields + [field_name]) if parent_fields else field_name


if __name__ == "__main__":
    # read list of spec.json files
    spec_files = sys.argv[1:]
    print(f'Spec files found: {len(spec_files)}')

    project_root_dir = os.path.abspath(os.curdir)
    spec_files = [os.path.join(project_root_dir, f) for f in spec_files]
    for file_path in spec_files:
        parse_spec(file_path)

    if ERRORS:
        exit(1)

