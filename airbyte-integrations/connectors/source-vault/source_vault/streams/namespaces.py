#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, List
import hvac

from .base import VaultStream


class Namespaces(VaultStream):
    """Stream for retrieving namespaces from Vault (Enterprise feature)."""
    
    @property
    def name(self) -> str:
        return "namespaces"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "path": {"type": ["string", "null"]},
                "parent_namespace": {"type": ["string", "null"]},
                "custom_metadata": {"type": ["object", "null"]},
            }
        }
    
    def _create_client_for_namespace(self, namespace_path: str) -> hvac.Client:
        """Create a new client configured for a specific namespace using the existing token."""
        vault_url = self.config["vault_url"]
        verify_ssl = self.config.get("verify_ssl", True)
        
        # Normalize client_namespace for HCP Vault (strip root prefix if present)
        client_namespace = None if namespace_path == "root" else namespace_path
        client = hvac.Client(
            url=vault_url,
            verify=verify_ssl,
            namespace=client_namespace
        )
        
        # Use the token from the main client (already authenticated)
        client.token = self.client.token
        
        return client
    
    def _list_namespaces_recursive(self, parent_path: str = "") -> List[Mapping[str, Any]]:
        """Recursively list all namespaces."""
        namespaces = []
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(parent_path if parent_path else self.vault_namespace)
            
            self.logger.debug(f"Listing namespaces at path: '{parent_path}'")
            list_response = client.sys.list_namespaces()
            
            if list_response and "data" in list_response:
                namespace_names = list_response["data"].get("keys", [])
                self.logger.debug(f"Found namespace keys at '{parent_path}': {namespace_names}")
                
                for ns_name in namespace_names:
                    # Clean namespace name (remove trailing slash)
                    ns_name = ns_name.rstrip('/')
                    
                    # Build full path
                    if parent_path:
                        full_path = f"{parent_path}/{ns_name}"
                    else:
                        full_path = ns_name
                    
                    self.logger.debug(f"Processing namespace: {full_path}")
                    
                    # Add this namespace
                    namespace_record = {
                        "id": full_path,
                        "path": full_path,
                        "parent_namespace": parent_path or None,
                        "custom_metadata": {},
                    }
                    
                    # Try to get additional metadata
                    try:
                        ns_detail = client.read(f"sys/namespaces/{ns_name}")
                            
                        if ns_detail and isinstance(ns_detail, dict) and "data" in ns_detail:
                            namespace_record["custom_metadata"] = ns_detail["data"].get("custom_metadata", {})
                    except Exception as e:
                        self.logger.debug(f"Could not read metadata for namespace {ns_name}: {e}")
                    
                    namespaces.append(namespace_record)
                    
                    # Recursively list child namespaces
                    self.logger.debug(f"Recursively scanning child namespaces of: {full_path}")
                    child_namespaces = self._list_namespaces_recursive(full_path)
                    namespaces.extend(child_namespaces)
            else:
                self.logger.debug(f"No namespaces found at path: '{parent_path}'")
                    
        except Exception as e:
            self.logger.debug(f"Error listing namespaces at '{parent_path}': {str(e)}")
            # Namespaces might not be available (non-Enterprise) or access denied
            
        return namespaces
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read namespaces from Vault."""
        # Always include the current/root namespace
        current_namespace = self.vault_namespace or "root"
        yield {
            "id": current_namespace,
            "path": current_namespace,
            "parent_namespace": None,
            "custom_metadata": {},
        }
        
        # List all child namespaces recursively starting from the root namespace
        self.logger.info(f"Starting recursive namespace discovery from: {self.vault_namespace}")
        namespaces = self._list_namespaces_recursive(self.vault_namespace)
        
        self.logger.info(f"Found {len(namespaces)} child namespaces")
        for namespace in namespaces:
            self.logger.debug(f"Yielding namespace: {namespace['path']}")
            yield namespace