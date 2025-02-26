#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import semver
from base_images import root_images
from base_images.python import bases


pytestmark = [
    pytest.mark.anyio,
]


class TestAirbytePythonConnectorBaseImage:
    @pytest.fixture
    def dummy_version(self):
        return semver.VersionInfo.parse("0.0.0-rc.1")

    def test_class_attributes(self):
        """Spot any regression in the class attributes."""
        assert bases.AirbytePythonConnectorBaseImage.root_image == root_images.PYTHON_3_11_11
        assert bases.AirbytePythonConnectorBaseImage.repository == "airbyte/python-connector-base"
        assert bases.AirbytePythonConnectorBaseImage.pip_cache_name == "pip_cache"

    async def test_run_sanity_checks(self, dagger_client, current_platform, dummy_version):
        base_image_version = bases.AirbytePythonConnectorBaseImage(dagger_client, dummy_version)
        await base_image_version.run_sanity_checks(current_platform)

    async def test_pip_cache_volume(self, dagger_client, current_platform, dummy_version):
        base_image_version = bases.AirbytePythonConnectorBaseImage(dagger_client, dummy_version)
        container = base_image_version.get_container(current_platform)
        assert "/custom_cache/pip" in await container.mounts()

    async def test_is_using_bookworm(self, dagger_client, current_platform, dummy_version):
        base_image_version = bases.AirbytePythonConnectorBaseImage(dagger_client, dummy_version)
        container = base_image_version.get_container(current_platform)
        cat_output = await container.with_exec(["cat", "/etc/os-release"]).stdout()
        assert "Debian GNU/Linux 12 (bookworm)" in [kv.split("=")[1].replace('"', "") for kv in cat_output.splitlines()]
