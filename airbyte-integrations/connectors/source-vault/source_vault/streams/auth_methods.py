#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional
import hvac

from .base import VaultStream


class AuthMethods(VaultStream):
    """Stream for retrieving auth methods from Vault across all namespaces."""
    
    @property
    def name(self) -> str:
        return "auth_methods"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "path": {"type": ["string", "null"]},
                "type": {"type": ["string", "null"]},
                "description": {"type": ["string", "null"]},
                "accessor": {"type": ["string", "null"]},
                "local": {"type": ["boolean", "null"]},
                "seal_wrap": {"type": ["boolean", "null"]},
                "external_entropy_access": {"type": ["boolean", "null"]},
                "options": {"type": ["object", "null"]},
                "config": {"type": ["object", "null"]},
                "uuid": {"type": ["string", "null"]},
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
        Each slice represents a namespace to scan for auth methods.
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
        """Read auth methods from Vault for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for auth methods in namespace: {namespace_path}")
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(namespace_path)
            
            # List all auth methods
            list_response = client.sys.list_auth_methods()
            
            if not list_response or "data" not in list_response:
                self.logger.debug(f"No auth methods found in namespace: {namespace_path}")
                return
            
            for path, data in list_response["data"].items():
                record = {
                    "path": path,
                    "type": data.get("type"),
                    "description": data.get("description"),
                    "accessor": data.get("accessor"),
                    "local": data.get("local"),
                    "seal_wrap": data.get("seal_wrap"),
                    "external_entropy_access": data.get("external_entropy_access"),
                    "options": data.get("options", {}),
                    "config": data.get("config", {}),
                    "uuid": data.get("uuid"),
                    "namespace_path": namespace_path,
                }
                
                yield record
                
        except Exception as e:
            self.logger.debug(f"Error listing auth methods in namespace {namespace_path}: {str(e)}")
            return 