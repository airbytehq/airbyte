# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Optional

import asyncclick as click

from pipelines.helpers.gcs import sanitize_gcp_credentials
from pipelines.models.secrets import InMemorySecretStore, Secret


def wrap_in_secret(ctx: click.Context, param: click.Option, value: Any) -> Optional[Secret]:  # noqa
    # Validate callback usage
    if value is None:
        return None
    assert param.name is not None
    if not isinstance(value, str):
        raise click.BadParameter(f"{param.name} value is not a string, only strings can be wrapped in a secret.")

    # Make sure the context object is set or set it with an empty dict
    ctx.ensure_object(dict)

    # Instantiate a global in memory secret store in the context object if it's not yet set
    if "secret_stores" not in ctx.obj:
        ctx.obj["secret_stores"] = {}
    if "in_memory" not in ctx.obj["secret_stores"]:
        ctx.obj["secret_stores"]["in_memory"] = InMemorySecretStore()

    # Add the CLI option value to the in memory secret store and wrap it in a Secret
    ctx.obj["secret_stores"]["in_memory"].add_secret(param.name, value)
    return Secret(param.name, ctx.obj["secret_stores"]["in_memory"])


def wrap_gcp_credentials_in_secret(ctx: click.Context, param: click.Option, value: Any) -> Optional[Secret]:  # noqa
    # Validate callback usage
    if value is None:
        return None
    if not isinstance(value, str):
        raise click.BadParameter(f"{param.name} value is not a string, only strings can be wrapped in a secret.")

    value = sanitize_gcp_credentials(value)
    return wrap_in_secret(ctx, param, value)
