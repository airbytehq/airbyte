#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


async def build(client, local_src, tag):
    connector_container = client.host().directory(local_src, exclude=[".venv"]).docker_build()
    return await connector_container.publish(tag)
