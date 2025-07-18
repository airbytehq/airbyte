#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import warnings

import pytest

from metadata_service import docker_hub


@pytest.fixture
def image_name():
    return "airbyte/source-faker"


def test_get_docker_hub_tags_and_digests(image_name):
    warnings.warn(f"This test can be flaky as its results depends on the current state of {image_name} dockerhub image.", UserWarning)
    tags_and_digests = docker_hub.get_docker_hub_tags_and_digests(image_name)
    assert isinstance(tags_and_digests, dict)
    assert "latest" in tags_and_digests, "The latest tag is not in the returned dict"
    assert "0.1.0" in tags_and_digests, f"The first {image_name} version is not in the returned dict"
    assert len(tags_and_digests) > 10, f"Pagination is likely not working as we expect more than 10 version of {image_name} to be released"


def test_get_latest_version_on_dockerhub(image_name):
    warnings.warn(f"This test can be flaky as its results depends on the current state of {image_name} dockerhub image.", UserWarning)
    assert (
        docker_hub.get_latest_version_on_dockerhub(image_name) is not None
    ), f"No latest version found for {image_name}. We expect one to exist."
