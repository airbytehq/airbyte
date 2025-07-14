#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional
import hvac

from .base import VaultStream


class Groups(VaultStream):
    """Stream for retrieving groups from Vault's identity system across all namespaces."""
    
    @property
    def name(self) -> str:
        return "groups"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "type": {"type": ["string", "null"]},
                "metadata": {"type": ["object", "null"]},
                "policies": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "member_entity_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "member_group_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "parent_group_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "namespace_id": {"type": ["string", "null"]},
                "namespace_path": {"type": ["string", "null"]},
                "creation_time": {"type": ["string", "null"]},
                "last_update_time": {"type": ["string", "null"]},
                "alias": {"type": ["object", "null"]},
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
        Each slice represents a namespace to scan for groups.
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
        """Read groups from Vault identity store for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for groups in namespace: {namespace_path}")
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(namespace_path)
            
            # List all groups
            list_response = client.secrets.identity.list_groups()
            
            if not list_response or "data" not in list_response:
                self.logger.debug(f"No groups found in namespace: {namespace_path}")
                return
            
            group_ids = list_response["data"].get("keys", [])
            self.logger.debug(f"Found {len(group_ids)} groups in namespace {namespace_path}")
            
            for group_id in group_ids:
                try:
                    # Read full group details
                    group_response = client.secrets.identity.read_group(group_id=group_id)
                    
                    if group_response and "data" in group_response:
                        group_data = group_response["data"]
                        
                        # Extract group record
                        record = {
                            "id": group_data.get("id"),
                            "name": group_data.get("name"),
                            "type": group_data.get("type"),
                            "metadata": group_data.get("metadata", {}),
                            "policies": group_data.get("policies", []),
                            "member_entity_ids": group_data.get("member_entity_ids", []),
                            "member_group_ids": group_data.get("member_group_ids", []),
                            "parent_group_ids": group_data.get("parent_group_ids", []),
                            "namespace_id": group_data.get("namespace_id"),
                            "namespace_path": namespace_path,
                            "creation_time": group_data.get("creation_time"),
                            "last_update_time": group_data.get("last_update_time"),
                            "alias": group_data.get("alias"),
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading group {group_id} in namespace {namespace_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error listing groups in namespace {namespace_path}: {str(e)}")
            return