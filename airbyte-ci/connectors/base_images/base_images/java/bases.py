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
from base_images.root_images import AMAZON_CORRETTO_21_AL_2023


class AirbyteJavaConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    root_image: Final[published_image.PublishedImage] = AMAZON_CORRETTO_21_AL_2023
    repository: Final[str] = "airbyte/java-connector-base"

    DD_AGENT_JAR_URL: Final[str] = "https://dtdg.co/latest-java-tracer"
    BASE_SCRIPT_URL = "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base/base.sh"
    JAVA_BASE_SCRIPT_URL: Final[str] = (
        "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base-java/javabase.sh"
    )

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container for the Java connector base image built with Docker.

        Args:
            platform (dagger.Platform): The platform this container should be built for.

        Returns:
            dagger.Container: The container for the base image.
        """
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.java-connector-base"
        
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
        for expected_rw_dir in [
            self.AIRBYTE_DIR_PATH,
            self.CACHE_DIR_PATH,
            "/tmp",
            "/secrets",
            "/config",
            "/usr/share/pki/ca-trust-source",
            "/etc/pki/ca-trust",
        ]:
            await base_sanity_checks.check_user_can_write_dir(container, self.USER, expected_rw_dir)
            await base_sanity_checks.check_user_can_read_dir(container, self.USER, expected_rw_dir)
        await base_sanity_checks.check_user_uid_guid(container, self.USER, self.USER_ID, self.USER_ID)
        await base_sanity_checks.check_file_exists(container, "/airbyte/dd-java-agent.jar")
        await base_sanity_checks.check_file_exists(container, "/airbyte/base.sh")
        await base_sanity_checks.check_file_exists(container, "/airbyte/javabase.sh")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
        await base_sanity_checks.check_env_var_with_printenv(container, "AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "tar")
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "openssl", "version")
