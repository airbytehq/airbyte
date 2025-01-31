# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import random
import string
from pathlib import Path

import pytest


@pytest.fixture
def random_string():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def connector(tmp_path, mocker, data_file):
    documentation_file_path = tmp_path / "documentation.md"

    connector = mocker.Mock(
        technical_name="test-connector",
        version="1.0.0",
        documentation_file_path=documentation_file_path,
        name="GitHub",
        ab_internal_sl=300,
        language="python",
        connector_type="source",
        metadata={"name": "GitHub"},
        name_from_metadata="GitHub",
        connector_spec_file_content={
            "connectionSpecification": {"required": ["repos"], "properties": {"repos": {"title": "GitHub Repositories"}}}
        },
    )
    with open(Path(__file__).parent / f"unit_tests/test_checks/data/docs/{data_file}.md", "r") as f:
        data = f.read().rstrip()
        connector.documentation_file_path.write_text(data)

    return connector


@pytest.fixture
def connector_with_invalid_links_in_documentation(tmp_path, mocker):
    return connector(tmp_path, mocker, "invalid_links")


@pytest.fixture
def connector_with_invalid_documentation(tmp_path, mocker):
    return connector(tmp_path, mocker, "incorrect_not_all_structure")


@pytest.fixture
def connector_with_correct_documentation(tmp_path, mocker):
    return connector(tmp_path, mocker, "correct")
