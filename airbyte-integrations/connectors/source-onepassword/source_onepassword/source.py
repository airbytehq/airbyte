#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import subprocess
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    AccountStream,
    VaultsStream,
    GroupsStream,
    ServiceAccountsStream,
    UsersStream,
    ItemsStream,
    GroupMembershipsStream
)

logger = logging.getLogger("airbyte")


class SourceOnepassword(AbstractSource):
    """
    Source connector for 1Password using the 1Password CLI
    """

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Test the connection to 1Password using the provided access token
        """
        try:
            # Set the access token as environment variable for the CLI
            import os
            env = os.environ.copy()
            env["OP_SERVICE_ACCOUNT_TOKEN"] = str(config["access_token"])
            
            # Try to run a simple 1Password CLI command to test the connection
            result = subprocess.run(
                ["op", "account", "get", "--format=json"],
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            
            # If the command succeeds, the connection is valid
            return True, None
            
        except subprocess.CalledProcessError as e:
            return False, f"Failed to connect to 1Password: {e.stderr}"
        except FileNotFoundError:
            return False, "1Password CLI (op) is not installed or not in PATH"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Return the list of streams available for this source
        """
        return [
            AccountStream(config),
            VaultsStream(config),
            GroupsStream(config),
            ServiceAccountsStream(config),
            UsersStream(config),
            ItemsStream(config),
            GroupMembershipsStream(config)
        ]