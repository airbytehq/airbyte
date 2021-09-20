import logging
import sys
import os
import json

# errors counter
ERRORS = 0
# required fields for each property field
FIELDS_TO_CHECK = {"title", "description"}
# configure logging format
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)

def parse_spec(spec_path: str):
    global ERRORS
    with open(spec_path) as json_file:
        data = json.load(json_file)

        try:
            props = data['connectionSpecification']['properties']
        except KeyError:
            logging.error(f"\033[1m{spec_path}\033[0m: Couldn't find properties in connector spec.json")
            ERRORS += 1
            return

        for field_name, property in props.items():
            if not FIELDS_TO_CHECK.issubset(property):
                logging.error(f"\033[1m{spec_path}\033[0m: Check failed for field \x1b[31;1m{field_name}\033[0m")
                ERRORS += 1

def validate_spec_field(spec_path, spec_object, field):
    global ERRORS
    for field_name, property in spec_object.items():
        if not FIELDS_TO_CHECK.issubset(property):
            logging.error(f"\033[1m{spec_path}\033[0m: Check failed for field \x1b[31;1m{field_name}\033[0m")
            ERRORS += 1

if __name__ == "__main__":
    spec_files = sys.argv[1:]
    print(f'Spec files found: {len(spec_files)}')

    project_root_dir = os.path.abspath(os.curdir)
    spec_files = [os.path.join(project_root_dir, f) for f in spec_files]
    for file_path in spec_files:
        parse_spec(file_path)

    if ERRORS != 0:
        exit(1)

