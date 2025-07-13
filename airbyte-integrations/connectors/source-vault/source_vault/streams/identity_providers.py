#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class IdentityProviders(VaultStream):
    """Stream for retrieving identity providers (OIDC) from Vault."""
    
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
                "namespace": {"type": ["string", "null"]},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read OIDC identity providers from Vault."""
        try:
            # List all OIDC providers
            list_response = self.client.secrets.identity.list_oidc_providers()
            
            if not list_response or "data" not in list_response:
                return
            
            provider_names = list_response["data"].get("keys", [])
            
            for provider_name in provider_names:
                try:
                    # Read provider details
                    provider_response = self.client.secrets.identity.read_oidc_provider(
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
                            "namespace": self.namespace,
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading OIDC provider {provider_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error listing OIDC providers: {str(e)}")
            # OIDC providers might not be configured
            return