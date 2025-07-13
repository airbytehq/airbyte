#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class Users(VaultStream):
    """Stream for retrieving users from Vault's identity system."""
    
    @property
    def name(self) -> str:
        return "users"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "metadata": {"type": ["object", "null"]},
                "policies": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "aliases": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["string", "null"]},
                            "mount_accessor": {"type": ["string", "null"]},
                            "mount_path": {"type": ["string", "null"]},
                            "mount_type": {"type": ["string", "null"]},
                            "name": {"type": ["string", "null"]},
                        }
                    }
                },
                "group_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "direct_group_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "inherited_group_ids": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "namespace_id": {"type": ["string", "null"]},
                "creation_time": {"type": ["string", "null"]},
                "last_update_time": {"type": ["string", "null"]},
                "disabled": {"type": ["boolean", "null"]},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read users from Vault identity store."""
        try:
            # List all entities (users)
            list_response = self.client.secrets.identity.list_entities()
            
            if not list_response or "data" not in list_response:
                return
            
            entity_ids = list_response["data"].get("keys", [])
            
            for entity_id in entity_ids:
                try:
                    # Read full entity details
                    entity_response = self.client.secrets.identity.read_entity(entity_id=entity_id)
                    
                    if entity_response and "data" in entity_response:
                        entity_data = entity_response["data"]
                        
                        # Extract user record
                        record = {
                            "id": entity_data.get("id"),
                            "name": entity_data.get("name"),
                            "metadata": entity_data.get("metadata", {}),
                            "policies": entity_data.get("policies", []),
                            "aliases": entity_data.get("aliases", []),
                            "group_ids": entity_data.get("group_ids", []),
                            "direct_group_ids": entity_data.get("direct_group_ids", []),
                            "inherited_group_ids": entity_data.get("inherited_group_ids", []),
                            "namespace_id": entity_data.get("namespace_id"),
                            "creation_time": entity_data.get("creation_time"),
                            "last_update_time": entity_data.get("last_update_time"),
                            "disabled": entity_data.get("disabled", False),
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading entity {entity_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error listing entities: {str(e)}")
            # Vault might not have identity engine enabled
            return