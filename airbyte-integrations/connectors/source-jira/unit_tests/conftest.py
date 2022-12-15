#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest

import json
import os

from pytest import fixture


@pytest.fixture
def config():
    return {
        "api_token": "token",
        "domain": "domain",
        "email": "email@email.com",
        "start_date": "2021-01-01T00:00:00Z",
        "projects": ["Project1", "Project2"]
    }


def load_file(fn):
    return open(os.path.join("unit_tests", "responses", fn)).read()


@fixture
def application_roles_response():
    return json.loads(load_file("application_role.json"))


@fixture
def boards_response():
    return json.loads(load_file("board.json"))


@fixture
def dashboards_response():
    return json.loads(load_file("dashboard.json"))


@fixture
def filters_response():
    return json.loads(load_file("filter.json"))


@fixture
def groups_response():
    return json.loads(load_file("groups.json"))


@fixture
def issue_fields_response():
    return json.loads(load_file("issue_fields.json"))


@fixture
def issues_field_configurations_response():
    return json.loads(load_file("issues_field_configurations.json"))


@fixture
def issues_link_types_response():
    return json.loads(load_file("issues_link_types.json"))


@fixture
def issues_navigator_settings_response():
    return json.loads(load_file("issues_navigator_settings.json"))


@fixture
def issue_notification_schemas_response():
    return json.loads(load_file("issue_notification_schemas.json"))


@fixture
def issue_properties_response():
    return json.loads(load_file("issue_properties.json"))


@fixture
def issue_resolutions_response():
    return json.loads(load_file("issue_resolutions.json"))


@fixture
def issue_security_schemes_response():
    return json.loads(load_file("issue_security_schemes.json"))


@fixture
def issue_type_schemes_response():
    return json.loads(load_file("issue_type.json"))
