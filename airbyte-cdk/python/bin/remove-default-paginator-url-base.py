#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import re


def get_all_manifest_paths(airbyte_integrations_path):
    for connectors_path, connectors, files in os.walk(os.path.join(airbyte_integrations_path, "connectors")):
        for connector in connectors:
            if connector.startswith("source-"):
                source_name = connector.replace("source-", "")
                manifest_path = os.path.join(connectors_path, connector, f"source_{source_name}", "manifest.yaml")
                if os.path.isfile(manifest_path):
                    yield manifest_path


def find_default_paginators(manifest_entity):
    if "type" in manifest_entity and manifest_entity["type"] == "DefaultPaginator":
        return [manifest_entity]

    default_paginators = []
    for key, value in manifest_entity.items():
        if isinstance(value, dict):
            default_paginators.extend(find_default_paginators(value))
    return default_paginators


def has_default_paginator(manifest_lines):
    return "DefaultPaginator" in "".join(manifest_lines)


def remove_lines(lines):
    """
    This is a very imperfect implementation of remove DefaultPaginator.url_base. It is flawed because:
    * If "type: DefaultPaginator" is after the property `url_base`, the property `url_base` will not be removed
    """
    line_iterator = iter(lines)
    while line := next(line_iterator, None):
        default_group_search = re.search('(\\s*)type:\\s"?DefaultPaginator', line)

        if default_group_search:
            loop_over_default_paginator_attributes = True
            default_paginator_properties_indentation = default_group_search.group(1)
            while loop_over_default_paginator_attributes:
                if default_paginator_properties_indentation not in line:
                    loop_over_default_paginator_attributes = False

                if "url_base" not in line:
                    yield line
                line = next(line_iterator, None)
        yield line


def rewrite_manifest(manifest_path):
    with open(manifest_path, "r") as manifest_file:
        manifest_lines = manifest_file.readlines()

    if not has_default_paginator(manifest_lines):
        return

    with open(manifest_path, "w") as manifest_file:
        for line in remove_lines(manifest_lines):
            manifest_file.write(line)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remove DefaultPaginator url_base")
    parser.add_argument("--path", help="airbyte-integrations folder")
    args = parser.parse_args()

    for path in get_all_manifest_paths(args.path):
        rewrite_manifest(path)
