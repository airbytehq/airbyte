#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Callable, Final

import dagger

from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.python import sanity_checks as python_sanity_checks
from base_images.root_images import PYTHON_3_11_8


class AirbyteManifestOnlyConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    """ManifestOnly base image class, only used to fetch the registry."""

    repository: Final[str] = "airbyte/source-declarative-manifest"


class AirbytePythonConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    root_image: Final[published_image.PublishedImage] = PYTHON_3_11_8
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
        def get_nltk_data_dir() -> dagger.Directory:
            """Returns a dagger directory containing the nltk data.

            Returns:
                dagger.Directory: A dagger directory containing the nltk data.
            """
            data_container = self.dagger_client.container().from_("bash:latest")

            for nltk_data_subfolder, nltk_data_urls in self.ntlk_data.items():
                full_nltk_data_path = f"{self.nltk_data_path}/{nltk_data_subfolder}"
                for nltk_data_url in nltk_data_urls:
                    zip_file = self.dagger_client.http(nltk_data_url)
                    data_container = (
                        data_container.with_file("/tmp/data.zip", zip_file)
                        .with_exec(["mkdir", "-p", full_nltk_data_path])
                        .with_exec(["unzip", "-o", "/tmp/data.zip", "-d", full_nltk_data_path])
                        .with_exec(["rm", "/tmp/data.zip"])
                    )
            return data_container.directory(self.nltk_data_path)

        def with_tesseract_and_poppler(container: dagger.Container) -> dagger.Container:
            """
            Installs Tesseract-OCR and Poppler-utils in the base image.
            These tools are necessary for OCR (Optical Character Recognition) processes and working with PDFs, respectively.
            """

            container = container.with_exec(
                ["sh", "-c", "apt-get update && apt-get install -y tesseract-ocr=5.3.0-2 poppler-utils=22.12.0-2+b1"]
            )

            return container

        def with_file_based_connector_dependencies(container: dagger.Container) -> dagger.Container:
            """
            Installs the dependencies for file-based connectors. This includes:
            - tesseract-ocr
            - poppler-utils
            - nltk data
            """
            container = with_tesseract_and_poppler(container)
            container = container.with_exec(["mkdir", "-p", "755", self.nltk_data_path]).with_directory(
                self.nltk_data_path, get_nltk_data_dir()
            )
            return container

        return with_file_based_connector_dependencies

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container used to build the base image.
        We currently use the python:3.9.18-slim-bookworm image as a base.
        We set the container system timezone to UTC.
        We then upgrade pip and install poetry.

        Args:
            platform (dagger.Platform): The platform this container should be built for.

        Returns:
            dagger.Container: The container used to build the base image.
        """
        pip_cache_volume: dagger.CacheVolume = self.dagger_client.cache_volume(AirbytePythonConnectorBaseImage.pip_cache_name)

        return (
            self.get_base_container(platform)
            .with_mounted_cache(self.pip_cache_path, pip_cache_volume, owner=self.USER)
            .with_env_variable("PIP_CACHE_DIR", self.pip_cache_path)
            # Upgrade pip to the expected version
            .with_exec(["pip", "install", "--upgrade", "pip==24.0", "setuptools==70.0.0"])
            # Declare poetry specific environment variables
            .with_env_variable("POETRY_VIRTUALENVS_CREATE", "false")
            .with_env_variable("POETRY_VIRTUALENVS_IN_PROJECT", "false")
            .with_env_variable("POETRY_NO_INTERACTION", "1")
            .with_exec(["pip", "install", "poetry==1.6.1"])
            .with_exec(["sh", "-c", "apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get clean"])
            .with_exec(["sh", "-c", "apt-get install -y socat=1.7.4.4-2"])
            # Install CDK system dependencies
            .with_(self.install_cdk_system_dependencies())
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
        await python_sanity_checks.check_python_version(container, "3.11.8")
        await python_sanity_checks.check_pip_version(container, "24.0")
        await base_sanity_checks.check_user_exists(container, self.USER, expected_uid=self.USER_ID, expected_gid=self.USER_ID)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.nltk_data_path)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.CACHE_DIR_PATH)
        await base_sanity_checks.check_user_can_write_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await base_sanity_checks.check_user_cant_write_dir(container, self.USER, self.CACHE_DIR_PATH)
        await python_sanity_checks.check_poetry_version(container, "1.6.1")
        await python_sanity_checks.check_python_image_has_expected_env_vars(container)
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "socat", "-V")
        await base_sanity_checks.check_socat_version(container, "1.7.4.4")
        await python_sanity_checks.check_cdk_system_dependencies(container)
