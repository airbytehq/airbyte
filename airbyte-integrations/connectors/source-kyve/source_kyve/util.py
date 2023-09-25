#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib
import os

import jsonref
from airbyte_cdk.sources.utils.schema_helpers import JsonFileLoader, ResourceSchemaLoader, resolve_ref_links


# We custom implemented the class to remove the requirement that $ref's have to be resolved from the 'shared folder'
class CustomResourceSchemaLoader(ResourceSchemaLoader):
    """JSONSchema loader from package resources"""

    def _resolve_schema_references(self, raw_schema: dict) -> dict:
        """
        Resolve links to external references and move it to local "definitions" map.

        :param raw_schema jsonschema to lookup for external links.
        :return JSON serializable object with references without external dependencies.
        """

        package = importlib.import_module(self.package_name)
        base = os.path.dirname(package.__file__) + "/"
        resolved = jsonref.JsonRef.replace_refs(raw_schema, loader=JsonFileLoader(base, "schemas/"), base_uri=base)
        resolved = resolve_ref_links(resolved)
        return resolved
