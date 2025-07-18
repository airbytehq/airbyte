#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Final

import dagger

from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.python import sanity_checks as python_sanity_checks
from base_images.root_images import PYTHON_3_11_13


class AirbyteManifestOnlyConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    """ManifestOnly base image class, only used to fetch the registry."""

    repository: Final[str] = "airbyte/source-declarative-manifest"

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container for the manifest-only connector base image.
        
        Args:
            platform (dagger.Platform): The platform this container should be built for.
            
        Returns:
            dagger.Container: The container for the base image.
        """
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.manifest-only-connector"
        
        return (
            self.dagger_client.container(platform=platform)
            .build(
                context=self.dagger_client.host().directory(str(docker_images_dir)),
                dockerfile=dockerfile_path.name
            )
        )

    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the manifest-only base image container.
        
        Args:
            platform (dagger.Platform): The platform on which the sanity checks should run.
        """
        container = self.get_container(platform)
        await base_sanity_checks.check_timezone_is_utc(container)
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
        await base_sanity_checks.check_user_exists(container, self.USER, expected_uid=self.USER_ID, expected_gid=self.USER_ID)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await base_sanity_checks.check_user_can_write_dir(container, self.USER, self.AIRBYTE_DIR_PATH)


class AirbytePythonConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    root_image: Final[published_image.PublishedImage] = PYTHON_3_11_13
    repository: Final[str] = "airbyte/python-connector-base"
    pip_cache_name: Final[str] = "pip_cache"
    nltk_data_path: Final[str] = "/usr/share/nltk_data"
    ntlk_data = {
        "tokenizers": {"https://github.com/nltk/nltk_data/raw/5db857e6f7df11eabb5e5665836db9ec8df07e28/packages/tokenizers/punkt.zip"},
        "taggers": {
            "https://github.com/nltk/nltk_data/raw/5db857e6f7df11eabb5e5665836db9ec8df07e28/packages/taggers/averaged_perceptron_tagger.zip"
        },
    }

    @property
    def pip_cache_path(self) -> str:
        return f"{self.CACHE_DIR_PATH}/pip"

    def install_cdk_system_dependencies(self) -> Callable:
        def with_file_based_connector_dependencies():
            """
            Placeholder for CDK system dependencies installation.
            This is now handled by the Dockerfile.
            """
            pass

        return with_file_based_connector_dependencies

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container for the Python connector base image built with Docker.

        Args:
            platform (dagger.Platform): The platform this container should be built for.

        Returns:
            dagger.Container: The container for the base image.
        """
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.python-connector-base"
        
        return (
            self.dagger_client.container(platform=platform)
            .build(
                context=self.dagger_client.host().directory(str(docker_images_dir)),
                dockerfile=dockerfile_path.name
            )
        )

    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (dagger.Platform): The platform on which the sanity checks should run.
        """
        container = self.get_container(platform)
        await base_sanity_checks.check_timezone_is_utc(container)
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
        await python_sanity_checks.check_python_version(container, "3.11.13")
        await python_sanity_checks.check_pip_version(container, "24.0")
        await base_sanity_checks.check_user_exists(container, self.USER, expected_uid=self.USER_ID, expected_gid=self.USER_ID)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.nltk_data_path)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.CACHE_DIR_PATH)
        await base_sanity_checks.check_user_can_write_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await python_sanity_checks.check_poetry_version(container, "1.8.4")
        await python_sanity_checks.check_python_image_has_expected_env_vars(container)
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "socat", "-V")
        await base_sanity_checks.check_socat_version(container, "1.7.4.4")
        await python_sanity_checks.check_cdk_system_dependencies(container)
