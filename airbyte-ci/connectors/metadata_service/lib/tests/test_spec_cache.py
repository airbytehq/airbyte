#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest

from metadata_service.spec_cache import CachedSpec, Registries, SpecCache, get_docker_info_from_spec_cache_path


@pytest.fixture
def mock_spec_cache():
    with (
        patch("google.cloud.storage.Client.create_anonymous_client") as MockClient,
        patch("google.cloud.storage.Client.bucket") as MockBucket,
    ):
        # Create stub mock client and bucket
        MockClient.return_value
        MockBucket.return_value

        # Create a list of 4 test CachedSpecs
        test_specs = [
            CachedSpec("image1", "tag-has-override", "path1", Registries.OSS),
            CachedSpec("image1", "tag-has-override", "path2", Registries.CLOUD),
            CachedSpec("image2", "tag-no-override", "path3", Registries.OSS),
            CachedSpec("image3", "tag-no-override", "path4", Registries.CLOUD),
        ]

        # Mock get_all_cached_specs to return test_specs
        with patch.object(SpecCache, "get_all_cached_specs", return_value=test_specs):
            yield SpecCache()


@pytest.mark.parametrize(
    "image,tag,given_registry,expected_registry",
    [
        ("image1", "tag-has-override", "OSS", Registries.OSS),
        ("image1", "tag-has-override", "CLOUD", Registries.CLOUD),
        ("image2", "tag-no-override", "OSS", Registries.OSS),
        ("image2", "tag-no-override", "CLOUD", Registries.OSS),
        ("image3", "tag-no-override", "OSS", None),
        ("image3", "tag-no-override", "CLOUD", Registries.CLOUD),
        ("nonexistent", "tag", "OSS", None),
        ("nonexistent", "tag", "CLOUD", None),
    ],
)
def test_find_spec_cache_with_fallback(mock_spec_cache, image, tag, given_registry, expected_registry):
    spec = mock_spec_cache.find_spec_cache_with_fallback(image, tag, given_registry)
    if expected_registry == None:
        assert spec == None
    else:
        assert spec.docker_repository == image
        assert spec.docker_image_tag == tag
        assert spec.registry == expected_registry


@pytest.mark.parametrize(
    "spec_cache_path,expected_spec",
    [
        (
            "specs/airbyte/destination-azure-blob-storage/0.1.1/spec.json",
            CachedSpec(
                "airbyte/destination-azure-blob-storage",
                "0.1.1",
                "specs/airbyte/destination-azure-blob-storage/0.1.1/spec.json",
                Registries.OSS,
            ),
        ),
        (
            "specs/airbyte/destination-azure-blob-storage/0.1.1/spec.cloud.json",
            CachedSpec(
                "airbyte/destination-azure-blob-storage",
                "0.1.1",
                "specs/airbyte/destination-azure-blob-storage/0.1.1/spec.cloud.json",
                Registries.CLOUD,
            ),
        ),
        (
            "specs/airbyte/source-azure-blob-storage/1.1.1/spec.json",
            CachedSpec(
                "airbyte/source-azure-blob-storage", "1.1.1", "specs/airbyte/source-azure-blob-storage/1.1.1/spec.json", Registries.OSS
            ),
        ),
        (
            "specs/faros/some-name/1.1.1/spec.json",
            CachedSpec("faros/some-name", "1.1.1", "specs/faros/some-name/1.1.1/spec.json", Registries.OSS),
        ),
    ],
)
def test_get_docker_info_from_spec_cache_path(spec_cache_path, expected_spec):
    actual_spec = get_docker_info_from_spec_cache_path(spec_cache_path)

    assert actual_spec.docker_repository == expected_spec.docker_repository
    assert actual_spec.docker_image_tag == expected_spec.docker_image_tag
    assert actual_spec.spec_cache_path == expected_spec.spec_cache_path
    assert actual_spec.registry == expected_spec.registry


def test_get_docker_info_from_spec_cache_path_invalid():
    with pytest.raises(Exception):
        get_docker_info_from_spec_cache_path("specs/airbyte/destination-azure-blob-storage/0.1.1/spec")
