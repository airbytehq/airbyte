#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os

from pytest import fixture


def load_file(fn):
    return open(os.path.join("unit_tests", "responses", fn)).read()


@fixture
def config_pass():
    return {"api_token": "goodtoken"}


@fixture
def projects_response():
    return json.loads(load_file("projects.json"))


@fixture
def project_memberships_response():
    return json.loads(load_file("project_memberships.json"))


@fixture
def activity_response():
    return json.loads(load_file("activity.json"))


@fixture
def labels_response():
    return json.loads(load_file("labels.json"))


@fixture
def releases_response():
    return json.loads(load_file("releases.json"))


@fixture
def epics_response():
    return json.loads(load_file("epics.json"))


@fixture
def stories_response():
    return json.loads(load_file("stories.json"))
