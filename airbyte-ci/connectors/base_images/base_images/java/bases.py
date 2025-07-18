#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Final

from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.root_images import AMAZON_CORRETTO_21_AL_2023


class AirbyteJavaConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    root_image: Final[published_image.PublishedImage] = AMAZON_CORRETTO_21_AL_2023
    repository: Final[str] = "airbyte/java-connector-base"

    DD_AGENT_JAR_URL: Final[str] = "https://dtdg.co/latest-java-tracer"
    BASE_SCRIPT_URL = "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base/base.sh"
    JAVA_BASE_SCRIPT_URL: Final[str] = (
        "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base-java/javabase.sh"
    )

    def get_container(self, platform: str) -> str:
        """Returns the image name for the Java connector base image built with Docker.

        Args:
            platform (str): The platform this container should be built for.

        Returns:
            str: The image name for the base image.
        """
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.java-connector-base"
        
        image_name = f"airbyte/java-connector-base:dev-{platform.replace('/', '-')}"
        
        cmd = [
            "docker", "build",
            "--platform", f"linux/{platform}",
            "--file", str(dockerfile_path),
            "--tag", image_name,
            str(docker_images_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build Java base image: {result.stderr}")
            
        return image_name

    async def run_sanity_checks(self, platform: str):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (str): The platform on which the sanity checks should run.
        """
        image_name = self.get_container(platform)
