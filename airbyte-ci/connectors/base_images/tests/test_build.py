#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from base_images import build, errors
from base_images.python import v1 as python_v1


@pytest.mark.anyio
async def test_run_sanity_checks_success(mocker, dagger_client, current_platform):
    class _0_0_0(python_v1._1_0_0):
        changelog_entry = "testing a base image version with successful sanity checks"

        @staticmethod
        async def run_sanity_checks(base_image_version):
            return None

    mocker.patch.object(build, "console")
    base_image_version = _0_0_0(dagger_client, current_platform)
    assert await build.run_sanity_checks(base_image_version)
    all_logs_calls = build.console.log.call_args_list
    assert all([call[0][0].startswith(":white_check_mark:") for call in all_logs_calls])


@pytest.mark.anyio
async def test_run_sanity_checks_failure(mocker, dagger_client, current_platform):
    class _0_0_0(python_v1._1_0_0):
        changelog_entry = "testing a base image version with failing sanity checks"

        @staticmethod
        async def run_sanity_checks(base_image_version):
            raise errors.SanityCheckError("mocked sanity check failure")

    mocker.patch.object(build, "console")
    base_image_version = _0_0_0(dagger_client, current_platform)
    assert not await build.run_sanity_checks(base_image_version)
    all_logs_calls = build.console.log.call_args_list
    assert all([call[0][0].startswith(":cross_mark:") for call in all_logs_calls])


@pytest.mark.anyio
async def test_generate_dockerfile(mocker, dagger_client, current_platform, tmp_path):
    class _0_0_0(python_v1._1_0_0):
        changelog_entry = "testing dockerfile generation"

    mocker.patch.object(build, "console")
    mocker.patch.object(build.consts, "PROJECT_DIR", tmp_path)
    base_image_version = _0_0_0(dagger_client, current_platform)
    build.generate_dockerfile(base_image_version)
    dockerfile_path = tmp_path / "generated" / "dockerfiles" / current_platform / f"{base_image_version.name_with_tag}.Dockerfile"
    assert dockerfile_path.exists()
    all_logs_calls = build.console.log.call_args_list
    assert all([call[0][0].startswith(":whale2: Generated Dockerfile") for call in all_logs_calls])


def test_write_changelog_file(tmp_path):
    changelog_path = tmp_path / "CHANGELOG.md"
    build.write_changelog_file(changelog_path, "test-image", {"0.0.0": python_v1._1_0_0})
    assert changelog_path.exists()
    changelog_content = changelog_path.read_text()
    assert changelog_content.startswith("# Changelog for test-image")
    assert python_v1._1_0_0.changelog_entry in changelog_content
