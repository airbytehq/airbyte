# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os

import pytest


@pytest.fixture
def oss_registry_dict():
    file_path = os.path.join(os.path.dirname(__file__), "oss_registry.json")
    return json.load(open(file_path))


@pytest.fixture
def cloud_registry_dict():
    file_path = os.path.join(os.path.dirname(__file__), "cloud_registry.json")
    return json.load(open(file_path))
