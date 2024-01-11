# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil

import pytest
from airbyte_lib.validate import validate


def test_validate_success():
    validate("./tests/integration_tests/fixtures/source-test", "./tests/integration_tests/fixtures/valid_config.json")

def test_validate_failure():
    with pytest.raises(Exception):
        validate("./tests/integration_tests/fixtures/source-test", "./tests/integration_tests/fixtures/invalid_config.json")
