#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import os
import sys
from json.decoder import JSONDecodeError

import click
from ci_common_utils import Logger

from . import SecretsManager

logger = Logger()

ENV_GCP_GSM_CREDENTIALS = "GCP_GSM_CREDENTIALS"


# credentials of GSM and GitHub secrets should be shared via shell environment
@click.command()
@click.argument("mode", type=click.Choice(("read", "write")))
@click.argument("connector_name")
def main(mode, connector_name) -> int:

    # parse unique connector name, because it can have the common prefix "connectors/<unique connector name>"
    connector_name = connector_name.split("/")[-1]
    if connector_name == "all":
        # if needed to load all secrets
        connector_name = None

    # parse GCP_GSM_CREDENTIALS
    try:
        gsm_credentials = json.loads(os.getenv(ENV_GCP_GSM_CREDENTIALS) or "{}")
    except JSONDecodeError as e:
        return logger.error(f"incorrect GCP_GSM_CREDENTIALS value, error: {e}")

    if not gsm_credentials:
        return logger.error("GCP_GSM_CREDENTIALS shouldn't be empty!")

    secret_manager = SecretsManager(
        connector_name=connector_name,
        gsm_credentials=gsm_credentials,
    )
    connector_secrets = secret_manager.read_from_gsm()
    if mode == "read":
        return secret_manager.write_to_storage(connector_secrets)
    if mode == "write":
        return secret_manager.update_secrets(connector_secrets)


if __name__ == "__main__":
    sys.exit(main())
