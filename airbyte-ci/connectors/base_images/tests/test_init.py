#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base_images
import pytest


def get_all_base_images_mock(successful_sanity_check: bool):
    all_base_images_failing_sanity_checks = {}
    for image_name, RealImage in base_images.ALL_BASE_IMAGES.items():

        class _0_0_0__success(RealImage):
            async def run_sanity_checks(self):
                pass

        class _0_0_0__failing(RealImage):
            async def run_sanity_checks(self):
                raise base_images.common.SanityCheckError("mocked sanity check failure")

        all_base_images_failing_sanity_checks[image_name] = _0_0_0__success if successful_sanity_check else _0_0_0__failing

    return all_base_images_failing_sanity_checks


@pytest.mark.anyio
@pytest.mark.parametrize("expect_success", [True, False])
async def test_run_all_sanity_checks(mocker, expect_success):
    mocker.patch.object(base_images, "console")
    mocker.patch.object(base_images, "ALL_BASE_IMAGES", get_all_base_images_mock(expect_success))
    successful = await base_images.run_all_sanity_checks(mocker.Mock())
    all_logs_calls = base_images.console.log.call_args_list
    if expect_success:
        assert all([call[0][0].startswith(":white_check_mark:") for call in all_logs_calls])
    else:
        assert all([call[0][0].startswith(":cross_mark:") for call in all_logs_calls])

    assert isinstance(successful, bool)
    assert successful == expect_success


def test_build_failing_sanity_checks(mocker):
    mocker.patch.object(base_images, "console")
    mocker.patch.object(base_images, "ALL_BASE_IMAGES", get_all_base_images_mock(successful_sanity_check=False))
    with pytest.raises(SystemExit) as excinfo:
        base_images.build()
    assert excinfo.value.code == 1
    all_logs_calls = base_images.console.log.call_args_list
    assert all_logs_calls[-1][0][0].startswith(":bomb: Sanity checks failed, aborting the build.")


def test_build_success_sanity_checks(mocker, tmp_path):
    mocker.patch.object(base_images, "console")
    mocker.patch.object(base_images.consts, "PROJECT_DIR", tmp_path)
    mocker.patch.object(base_images, "ALL_BASE_IMAGES", get_all_base_images_mock(successful_sanity_check=True))
    base_images.build()
    all_logs_calls = base_images.console.log.call_args_list
    expected_changelog_path = tmp_path / "CHANGELOG_PYTHON_CONNECTOR_BASE_IMAGE.md"
    assert expected_changelog_path.exists()
    assert expected_changelog_path.is_file()
    assert expected_changelog_path.stat().st_size > 0
    assert all_logs_calls[-2][0][0].startswith(":tada: Successfully ran sanity checks")
    assert all_logs_calls[-1][0][0].startswith(":memo: Wrote the updated changelog")
