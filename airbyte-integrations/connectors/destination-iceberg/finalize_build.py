#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# This function is async in case async operations are needed.
async def finalize_build(connector_context, connector_container, *args, **kwargs):
    custom_java_opts = "--add-opens java.base/java.lang=ALL-UNNAMED \
    --add-opens java.base/java.util=ALL-UNNAMED \
    --add-opens java.base/java.lang.reflect=ALL-UNNAMED \
    --add-opens java.base/java.text=ALL-UNNAMED \
    --add-opens java.base/sun.nio.ch=ALL-UNNAMED \
    --add-opens java.base/java.nio=ALL-UNNAMED "
    return connector_container.with_env_variable("JAVA_OPTS", custom_java_opts)
