#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
async def get_python_connector_image_tarball(context):
    host_tarball_path = f"/tmp/{context.connector.technical_name}.tar"
    await (context.get_connector_dir(exclude=[".venv", "secrets"]).docker_build().export(host_tarball_path))
    return host_tarball_path
