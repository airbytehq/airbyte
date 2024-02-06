# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil

import pytest
from airbyte_lib.validate import validate


@pytest.fixture(scope="module", autouse=True)
def autouse_source_test_installation(source_test_installation):
    return


@pytest.fixture(scope="function", autouse=True)
def autouse_source_test_registry(source_test_registry):
    return


def test_validate_success():
    validate("./tests/integration_tests/fixtures/source-test", "./tests/integration_tests/fixtures/valid_config.json", validate_install_only=False)

def test_validate_check_failure():
    with pytest.raises(Exception):
        validate("./tests/integration_tests/fixtures/source-test", "./tests/integration_tests/fixtures/invalid_config.json", validate_install_only=False)

def test_validate_success_install_only():
    validate("./tests/integration_tests/fixtures/source-test", "./tests/integration_tests/fixtures/invalid_config.json", validate_install_only=True)

def test_validate_config_failure():
    with pytest.raises(Exception):
        validate("./tests/integration_tests/fixtures/source-broken", "./tests/integration_tests/fixtures/valid_config.json", validate_install_only=True)
