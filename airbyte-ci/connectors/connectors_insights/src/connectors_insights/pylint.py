# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from connector_ops.utils import ConnectorLanguage  # type: ignore

from connectors_insights.utils import never_fail_exec

if TYPE_CHECKING:
    import dagger
    from connector_ops.utils import Connector  # type: ignore

PYLINT_COMMAND = [
    "pylint",
    "--load-plugins=custom_plugin",
    "--disable=all",
    "--output-format=json",
    "--enable=deprecated-class",
    "--enable=deprecated-module",
    "--enable=forbidden-method-name",
    ".",
]


async def get_pylint_output(dagger_client: dagger.Client, connector: Connector) -> str | None:
    """Invoke pylint to check for deprecated classes and modules in the connector code.
    We use the custom plugin cdk_deprecation_checkers.py to check for deprecated classes and modules.
    The plugin is located in the `pylint_plugins` directory.

    Args:
        dagger_client (dagger.Client): Current dagger client.
        connector (Connector): Connector object.

    Returns:
        str | None: Pylint output.
    """
    if connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE, ConnectorLanguage.MANIFEST_ONLY]:
        return None
    cdk_deprecation_checker_path = Path(os.path.abspath(__file__)).parent / "pylint_plugins/cdk_deprecation_checkers.py"
    pip_cache_volume: dagger.CacheVolume = dagger_client.cache_volume("pip_cache")

    return await (
        dagger_client.container()
        .from_(connector.image_address)
        .with_user("root")
        .with_mounted_cache("/root/.cache/pip", pip_cache_volume)
        .with_new_file("__init__.py", contents="")
        .with_exec(["pip", "install", "pylint"])
        .with_workdir(connector.technical_name.replace("-", "_"))
        .with_env_variable("PYTHONPATH", ".")
        .with_new_file("custom_plugin.py", contents=cdk_deprecation_checker_path.read_text())
        .with_(never_fail_exec(PYLINT_COMMAND))
        .stdout()
    )
