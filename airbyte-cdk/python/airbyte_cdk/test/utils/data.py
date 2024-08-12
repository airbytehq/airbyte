# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import get_unit_test_folder


def read_resource_file_contents(resource: str, test_location: str) -> str:
    """Read the contents of a test data file from the test resource folder."""
    file_path = str(get_unit_test_folder(test_location) / "resource" / "http" / "response" / f"{resource}")
    with open(file_path) as f:
        response = f.read()
    return response
