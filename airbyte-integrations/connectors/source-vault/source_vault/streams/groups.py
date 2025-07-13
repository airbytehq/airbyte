#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class Groups(VaultStream):
    """Stream for retrieving groups from Vault's identity system."""
    
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
                "creation_time": {"type": ["string", "null"]},
                "last_update_time": {"type": ["string", "null"]},
                "alias": {
                    "type": ["object", "null"],
                    "properties": {
                        "id": {"type": ["string", "null"]},
                        "name": {"type": ["string", "null"]},
                        "mount_accessor": {"type": ["string", "null"]},
                        "mount_path": {"type": ["string", "null"]},
                        "mount_type": {"type": ["string", "null"]},
                    }
                }
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read groups from Vault identity store."""
        try:
            # List all groups
            list_response = self.client.secrets.identity.list_groups()
            
            if not list_response or "data" not in list_response:
                return
            
            group_ids = list_response["data"].get("keys", [])
            
            for group_id in group_ids:
                try:
                    # Read full group details
                    group_response = self.client.secrets.identity.read_group(group_id=group_id)
                    
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
                            "creation_time": group_data.get("creation_time"),
                            "last_update_time": group_data.get("last_update_time"),
                            "alias": group_data.get("alias"),
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading group {group_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error listing groups: {str(e)}")
            # Vault might not have identity engine enabled
            return