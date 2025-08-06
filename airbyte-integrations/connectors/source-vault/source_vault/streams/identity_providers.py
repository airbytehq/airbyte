#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional
import hvac

from .base import VaultStream


class IdentityProviders(VaultStream):
    """Stream for retrieving identity providers (OIDC) from Vault across all namespaces."""
    
    @property
    def name(self) -> str:
        return "identity_providers"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "issuer": {"type": ["string", "null"]},
                "issuer_ca_pem": {"type": ["string", "null"]},
                "allowed_client_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "scopes_supported": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "namespace_path": {"type": ["string", "null"]},
            }
        }
    
    def _create_client_for_namespace(self, namespace_path: str) -> hvac.Client:
        """Create a new client configured for a specific namespace using the existing token."""
        vault_url = self.config["vault_url"]
        verify_ssl = self.config.get("verify_ssl", True)
        
        # Create client with specific namespace
        client_namespace = None if namespace_path == "root" else namespace_path
        
        client = hvac.Client(
            url=vault_url,
            verify=verify_ssl,
            namespace=client_namespace
        )
        
        # Use the token from the main client (already authenticated)
        client.token = self.client.token
        
        return client
    
    def stream_slices(
        self, sync_mode, cursor_field: Optional[str] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Generate stream slices based on namespaces.
        Each slice represents a namespace to scan for identity providers.
        """
        # Import here to avoid circular imports
        from .namespaces import Namespaces
        
        # Create namespaces stream to get all namespaces
        namespaces_stream = Namespaces(
            client=self.client, 
            config=self.config, 
            vault_namespace=self.vault_namespace
        )
        
        # Get all namespaces
        namespace_records = list(namespaces_stream.read_records(sync_mode))
        
        self.logger.info(f"Creating stream slices for {len(namespace_records)} namespaces")
        
        # Create a slice for each namespace
        for namespace_record in namespace_records:
            namespace_path = namespace_record["path"]
            self.logger.debug(f"Creating slice for namespace: {namespace_path}")
            
            yield {
                "namespace_path": namespace_path,
                "namespace_id": namespace_record["id"]
            }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read OIDC identity providers from Vault for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for identity providers in namespace: {namespace_path}")
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(namespace_path)
            
            # List all OIDC providers
            list_response = client.secrets.identity.list_oidc_providers()
            
            if not list_response or "data" not in list_response:
                self.logger.debug(f"No identity providers found in namespace: {namespace_path}")
                return
            
            provider_names = list_response["data"].get("keys", [])
            self.logger.debug(f"Found {len(provider_names)} identity providers in namespace {namespace_path}")
            
            for provider_name in provider_names:
                try:
                    # Read provider details
                    provider_response = client.secrets.identity.read_oidc_provider(
                        name=provider_name
                    )
                    
                    if provider_response and "data" in provider_response:
                        provider_data = provider_response["data"]
                        
                        # Extract provider record
                        record = {
                            "id": provider_name,
                            "name": provider_name,
                            "issuer": provider_data.get("issuer"),
                            "issuer_ca_pem": provider_data.get("issuer_ca_pem"),
                            "allowed_client_ids": provider_data.get("allowed_client_ids", []),
                            "scopes_supported": provider_data.get("scopes_supported", []),
                            "namespace_path": namespace_path,
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading OIDC provider {provider_name} in namespace {namespace_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error listing OIDC providers in namespace {namespace_path}: {str(e)}")
            # OIDC providers might not be configured
            return