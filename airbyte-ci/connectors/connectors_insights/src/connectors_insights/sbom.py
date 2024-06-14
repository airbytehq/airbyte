# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    import dagger
    from connector_ops.utils import Connector  # type: ignore

SYFT_DOCKER_IMAGE = "anchore/syft:v1.6.0"
GRYPE_DOCKER_IMAGE = "anchore/grype:v0.78.0"


def get_syft_container(dagger_client: dagger.Client) -> dagger.Container:
    return (
        dagger_client.container().from_(SYFT_DOCKER_IMAGE)
        # Syft requires access to the docker daemon. We share the host's docker socket with the Syft container.
        .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
    )


async def get_text_sbom(dagger_client: dagger.Client, connector: Connector) -> str:
    """Generate a SBOM in text format for the given connector.

    Args:
        dagger_client (dagger.Client): The Dagger client to use.
        connector (Connector): The connector to generate the SBOM for.

    Returns:
        str: The SBOM in text format.
    """
    syft_container = get_syft_container(dagger_client)
    return await syft_container.with_exec([connector.image_address, "-o", "syft-text"]).stdout()


async def get_json_sbom(dagger_client: dagger.Client, connector: Connector) -> str:
    """Use Syft to generate a SBOM in JSON format for the given connector.

    Args:
        dagger_client (dagger.Client): The Dagger client to use.
        connector (Connector): The connector to generate the SBOM for.

    Returns:
        str: The SBOM in JSON format.
    """
    syft_container = get_syft_container(dagger_client)
    return await syft_container.with_exec([connector.image_address, "-o", "syft-json"]).stdout()
