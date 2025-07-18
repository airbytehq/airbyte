#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Final

from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.python import sanity_checks as python_sanity_checks
from base_images.root_images import PYTHON_3_11_13


class AirbyteManifestOnlyConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    """ManifestOnly base image class, only used to fetch the registry."""

    repository: Final[str] = "airbyte/source-declarative-manifest"


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

    def get_container(self, platform: str) -> str:
        """Returns the image name for the Python connector base image built with Docker.

        Args:
            platform (str): The platform this container should be built for.

        Returns:
            str: The image name for the base image.
        """
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.python-connector-base"
        
        image_name = f"airbyte/python-connector-base:dev-{platform.replace('/', '-')}"
        
        cmd = [
            "docker", "build",
            "--platform", f"linux/{platform}",
            "--file", str(dockerfile_path),
            "--tag", image_name,
            str(docker_images_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build Python base image: {result.stderr}")
            
        return image_name

    async def run_sanity_checks(self, platform: str):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (str): The platform on which the sanity checks should run.
        """
        image_name = self.get_container(platform)
