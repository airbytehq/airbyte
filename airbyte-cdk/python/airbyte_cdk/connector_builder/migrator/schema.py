#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, Optional

import jsonref
from airbyte_cdk.sources.utils.schema_helpers import JsonFileLoader


class SchemaResolver:
    def resolve(self, python_package_path: str, stream_name: str) -> Optional[Any]:
        """
        In theory, any manifest can mentioned any path for the schemas. However, this class assumes that `file_path` is always undefined of
        matching "./{source_name}/schemas/{stream_name}.json"
        """
        schemas_path = os.path.join(python_package_path, "schemas")
        stream_schema_path = os.path.join(schemas_path, f"{stream_name}.json")
        if os.path.exists(stream_schema_path):
            with open(stream_schema_path, "r") as schema_file:
                unresolved_schema = json.load(schema_file)

            if os.path.exists(os.path.join(schemas_path, "shared")):
                return jsonref.JsonRef.replace_refs(
                    unresolved_schema,
                    loader=JsonFileLoader(python_package_path, "schemas/shared"),
                    # We need to have the "/" at the end because else, the last part in the path is not considered a dir and is
                    # dropped (see https://github.com/python/cpython/blob/b1de3807b832b72dfeb66dd5646159d08d2cc74a/Lib/urllib/parse.py#L570-L573)
                    base_uri=python_package_path + "/"
                )
            return unresolved_schema
        return None
