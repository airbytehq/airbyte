#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from contextlib import contextmanager

import pytest


@pytest.fixture
def mssql_spec_schema():
    with open("unit_tests/data/mssql_spec.json") as f:
        return json.load(f).get("connectionSpecification")


@pytest.fixture
def postgres_source_spec_schema():
    with open("unit_tests/data/postgres_spec.json") as f:
        return json.load(f).get("connectionSpecification")


@contextmanager
def does_not_raise():
    yield
