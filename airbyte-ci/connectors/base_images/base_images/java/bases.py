#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Callable, Final

import dagger

from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.python import sanity_checks as python_sanity_checks
from base_images.root_images import AMAZON_CORRETTO_21_AL_2023
from base_images.utils.dagger import sh_dash_c


class AirbyteJavaConnectorBaseImage(bases.AirbyteConnectorBaseImage):
    # TODO: remove this once we want to build the base image with the airbyte user.
    USER: Final[str] = "root"

    root_image: Final[published_image.PublishedImage] = AMAZON_CORRETTO_21_AL_2023
    repository: Final[str] = "airbyte/java-connector-base"

    DD_AGENT_JAR_URL: Final[str] = "https://dtdg.co/latest-java-tracer"
    BASE_SCRIPT_URL = "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base/base.sh"
    JAVA_BASE_SCRIPT_URL: Final[str] = (
        "https://raw.githubusercontent.com/airbytehq/airbyte/6d8a3a2bc4f4ca79f10164447a90fdce5c9ad6f9/airbyte-integrations/bases/base-java/javabase.sh"
    )

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container used to build the base image for java connectors
        We currently use the Amazon coretto image as a base.
        We install some packages required to build java connectors.
        We also download the datadog java agent jar and the javabase.sh script.
        We set some env variables used by the javabase.sh script.

        Args:
            platform (dagger.Platform): The platform this container should be built for.

        Returns:
            dagger.Container: The container used to build the base image.
        """

        return (
            # TODO: Call this when we want to build the base image with the airbyte user
            # self.get_base_container(platform)
            self.dagger_client.container(platform=platform)
            .from_(self.root_image.address)
            # Bundle RUN commands together to reduce the number of layers.
            .with_exec(
                sh_dash_c(
                    [
                        # Update first, but in the same .with_exec step as the package installation.
                        # Otherwise, we risk caching stale package URLs.
                        "yum update -y --security",
                        # tar is equired to untar java connector binary distributions.
                        # openssl is required because we need to ssh and scp sometimes.
                        # findutils is required for xargs, which is shipped as part of findutils.
                        f"yum install -y tar openssl findutils",
                        # Remove any dangly bits.
                        "yum clean all",
                    ]
                )
            )
            .with_workdir("/airbyte")
            # Copy the datadog java agent jar from the internet.
            .with_file("dd-java-agent.jar", self.dagger_client.http(self.DD_AGENT_JAR_URL))
            # Copy base.sh from the git repo.
            .with_file("base.sh", self.dagger_client.http(self.BASE_SCRIPT_URL))
            # Copy javabase.sh from the git repo.
            .with_file("javabase.sh", self.dagger_client.http(self.JAVA_BASE_SCRIPT_URL))
            # Set a bunch of env variables used by base.sh.
            .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
            .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
            .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
            .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
            .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
            .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
            .with_entrypoint(["/airbyte/base.sh"])
        )

    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (dagger.Platform): The platform on which the sanity checks should run.
        """
        container = self.get_container(platform)
        await base_sanity_checks.check_user_can_read_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
        await base_sanity_checks.check_user_can_write_dir(container, self.USER, self.AIRBYTE_DIR_PATH)
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
