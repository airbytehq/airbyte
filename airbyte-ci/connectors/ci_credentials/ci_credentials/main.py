#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

import click
from common_utils import Logger

from . import SecretsManager
from .library import get_secrets_manager

logger = Logger()

ENV_GCP_GSM_CREDENTIALS = "GCP_GSM_CREDENTIALS"


# credentials of GSM and GitHub secrets should be shared via shell environment
@click.group()
@click.argument("connector_name")
@click.option("--gcp-gsm-credentials", envvar="GCP_GSM_CREDENTIALS")
@click.pass_context
def ci_credentials(ctx, connector_name: str, gcp_gsm_credentials):
    ctx.ensure_object(dict)
    ctx.obj["connector_name"] = connector_name
    # parse unique connector name, because it can have the common prefix "connectors/<unique connector name>"
    connector_name = connector_name.split("/")[-1]
    if connector_name == "all":
        # if needed to load all secrets
        connector_name = None

    secret_manager: SecretsManager = get_secrets_manager(
        connector_name=connector_name,
        gcp_gsm_credentials=gcp_gsm_credentials,
    )
    ctx.obj["secret_manager"] = secret_manager
    ctx.obj["connector_secrets"] = secret_manager.read_from_gsm()


@ci_credentials.command(help="Download GSM secrets locally to the connector's secrets directory.")
@click.pass_context
def write_to_storage(ctx):
    written_files = ctx.obj["secret_manager"].write_to_storage(ctx.obj["connector_secrets"])
    written_files_count = len(written_files)
    click.echo(f"{written_files_count} secret files were written: {','.join([str(path) for path in written_files])}")


@ci_credentials.command(help="Update GSM secrets according to the content of the secrets/updated_configurations directory.")
@click.pass_context
def update_secrets(ctx):
    new_remote_secrets = ctx.obj["secret_manager"].update_secrets(ctx.obj["connector_secrets"])
    updated_secret_names = [secret.name for secret in new_remote_secrets]
    updated_secrets_count = len(new_remote_secrets)
    click.echo(f"Updated {updated_secrets_count} secrets: {','.join(updated_secret_names)}")


if __name__ == "__main__":
    sys.exit(ci_credentials(obj={}))
