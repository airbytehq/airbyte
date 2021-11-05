#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json

import pytest


@pytest.fixture
def mssql_spec_schema():
    with open("unit_tests/data/mssql_spec.json") as f:
        return json.load(f).get("connectionSpecification")


@pytest.fixture
def postgres_source_spec_schema():
    with open("unit_tests/data/postgres_spec.json") as f:
        return json.load(f).get("connectionSpecification")
