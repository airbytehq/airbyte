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
            self.dagger_client.container(platform=platform)
            .from_(self.root_image.address)
            # Bundle RUN commands together to reduce the number of layers.
            .with_exec(
                sh_dash_c(
                    [
                        # Shadow-utils is required to add a user with a specific UID and GID.
                        # tar is equired to untar java connector binary distributions.
                        # openssl is required because we need to ssh and scp sometimes.
                        # findutils is required for xargs, which is shipped as part of findutils.
                        f"yum install -y shadow-utils tar openssl findutils",
                        # Update first, but in the same .with_exec step as the package installation.
                        # Otherwise, we risk caching stale package URLs.
                        "yum update -y --security",
                        # Remove any dangly bits.
                        "yum clean all",
                        # Remove the yum cache to reduce the image size.
                        "rm -rf /var/cache/yum",
                        # Create the group 'airbyte' with the GID 1000
                        f"groupadd --gid {self.USER_ID} {self.USER}",
                        # Create the user 'airbyte' with the UID 1000
                        f"useradd --uid {self.USER_ID} --gid {self.USER} --shell /bin/bash --create-home {self.USER}",
                        # Create mount point for secrets and configs
                        "mkdir /secrets",
                        "mkdir /config",
                        # Create the cache airbyte directories and set the right permissions
                        f"mkdir --mode 755 {self.AIRBYTE_DIR_PATH}",
                        f"mkdir --mode 755 {self.CACHE_DIR_PATH}",
                        # Change the owner of the airbyte directory to the user 'airbyte'
                        f"chown -R {self.USER}:{self.USER} {self.AIRBYTE_DIR_PATH}",
                        f"chown -R {self.USER}:{self.USER} {self.CACHE_DIR_PATH}",
                        f"chown -R {self.USER}:{self.USER} /secrets",
                        f"chown -R {self.USER}:{self.USER} /config",
                        f"chown -R {self.USER}:{self.USER} /usr/share/pki/ca-trust-source",
                        f"chown -R {self.USER}:{self.USER} /etc/pki/ca-trust",
                        f"chown -R {self.USER}:{self.USER} /tmp",
                    ]
                )
            )
            .with_workdir(self.AIRBYTE_DIR_PATH)
            # Copy the datadog java agent jar from the internet.
            .with_file("dd-java-agent.jar", self.dagger_client.http(self.DD_AGENT_JAR_URL), owner=self.USER)
            # Copy base.sh from the git repo.
            .with_file("base.sh", self.dagger_client.http(self.BASE_SCRIPT_URL), owner=self.USER)
            # Copy javabase.sh from the git repo.
            .with_file("javabase.sh", self.dagger_client.http(self.JAVA_BASE_SCRIPT_URL), owner=self.USER)
            # Set a bunch of env variables used by base.sh.
            .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
            .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
            .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
            .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
            .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
            .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
            .with_entrypoint(["/airbyte/base.sh"])
            .with_user(self.USER)
        )

    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (dagger.Platform): The platform on which the sanity checks should run.
        """
        container = await self.get_container(platform)
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
