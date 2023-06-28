#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import sys

import pytest

CONNECTION_SPECIFICATION = {
    "type": "object",
    "additionalProperties": True,
}


@pytest.fixture
def json_spec():
    # Our way of resolving the absolute path to root of the airbyte-cdk unit test directory where spec.yaml files should
    # be written to (i.e. ~/airbyte/airbyte-cdk/python/unit-tests) because that is where they are read from during testing.
    module = sys.modules[__name__]
    module_path = os.path.abspath(module.__file__)
    test_path = os.path.dirname(module_path)
    spec_root = test_path.split("/sources/file_based")[0]

    spec = {
        "documentationUrl": "https://airbyte.com/#yaml-from-external",
        "connectionSpecification": CONNECTION_SPECIFICATION,
    }

    json_path = os.path.join(spec_root, "spec.json")
    with open(json_path, "w") as f:
        f.write(json.dumps(spec))
    yield
    os.remove(json_path)
