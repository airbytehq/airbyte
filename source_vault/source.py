#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import hvac
from airbyte_cdk import AbstractSource
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.streams import Stream

from .streams import (
    Groups,
    IdentityProviders,
    Namespaces,
    Policies,
    Roles,
    Secrets,
    Users,
    VaultInfo,
)


class SourceVault(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Tests if the connection is working.
        """
        try:
            client = self._get_vault_client(config)
            
            # Test authentication
            if not client.is_authenticated():
                return False, "Failed to authenticate with Vault using provided credentials"
            
            # Test basic access
            try:
                client.sys.read_health_status(method="GET")
                return True, None
            except Exception as e:
                return False, f"Failed to connect to Vault: {str(e)}"
                
        except Exception as e:
            return False, f"Error connecting to Vault: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns the list of streams to sync.
        """
        client = self._get_vault_client(config)
        namespace = config.get("namespace", "")
        
        return [
            VaultInfo(client=client, config=config),
            Users(client=client, config=config, namespace=namespace),
            Roles(client=client, config=config, namespace=namespace),
            Policies(client=client, config=config, namespace=namespace),
            Groups(client=client, config=config, namespace=namespace),
            Namespaces(client=client, config=config, namespace=namespace),
            Secrets(client=client, config=config, namespace=namespace),
            IdentityProviders(client=client, config=config, namespace=namespace),
        ]

    def _get_vault_client(self, config: Mapping[str, Any]) -> hvac.Client:
        """
        Creates and configures a Vault client.
        """
        vault_url = config["vault_url"]
        role_id = config["role_id"]
        secret_id = config["secret_id"]
        verify_ssl = config.get("verify_ssl", True)
        namespace = config.get("namespace", "")
        
        # Initialize client
        client = hvac.Client(
            url=vault_url,
            verify=verify_ssl,
            namespace=namespace if namespace else None
        )
        
        # Authenticate using AppRole
        client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id
        )
        
        return client