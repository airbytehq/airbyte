# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from conftest import get_source


@pytest.mark.parametrize("field_name", ["domains", "exclude_domains"])
def test_domain_descriptions_use_correct_spelling(field_name):
    spec = get_source(config={}).spec(logging.getLogger("airbyte"))
    description = spec.connectionSpecification["properties"][field_name]["description"]

    assert "comma-separated" in description
    assert "seperated" not in description


def test_connection_specification_has_no_spelling_error():
    spec = get_source(config={}).spec(logging.getLogger("airbyte"))

    assert "seperated" not in json.dumps(spec.connectionSpecification)
