#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class VaultInfo(VaultStream):
    """Stream for retrieving core information about the Vault instance."""
    
    @property
    def name(self) -> str:
        return "vault_info"
    
    @property
    def primary_key(self) -> Optional[str]:
        return None
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                # Basic cluster information
                "cluster_id": {"type": ["string", "null"]},
                "cluster_name": {"type": ["string", "null"]},
                "version": {"type": ["string", "null"]},
                "initialized": {"type": ["boolean", "null"]},
                "sealed": {"type": ["boolean", "null"]},
                "standby": {"type": ["boolean", "null"]},
                "performance_standby": {"type": ["boolean", "null"]},
                "replication_performance_mode": {"type": ["string", "null"]},
                "replication_dr_mode": {"type": ["string", "null"]},
                "server_time_utc": {"type": ["string", "null"]},
                "namespace": {"type": ["string", "null"]},
                
                # Leader information
                "leader_address": {"type": ["string", "null"]},
                "leader_cluster_address": {"type": ["string", "null"]},
                "is_leader": {"type": ["boolean", "null"]},
                "ha_enabled": {"type": ["boolean", "null"]},
                
                # Build information
                "build_date": {"type": ["string", "null"]},
                "go_version": {"type": ["string", "null"]},
                
                # System metadata
                "warnings": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                }
            }
        }
    
    def _safe_get_data(self, response) -> dict:
        """Safely extract data from various response formats."""
        if hasattr(response, 'json') and callable(response.json):
            try:
                result = response.json()
                return result if isinstance(result, dict) else {}
            except:
                return {}
        elif isinstance(response, dict):
            return response
        else:
            return {}
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read core Vault system information."""
        record = {
            "namespace": self.vault_namespace or "root"
        }
        
        # Get seal status - this is the most reliable endpoint
        try:
            seal_response = self.client.sys.read_seal_status()
            seal_data = self._safe_get_data(seal_response)
            
            record.update({
                "cluster_id": seal_data.get("cluster_id"),
                "cluster_name": seal_data.get("cluster_name"),
                "version": seal_data.get("version"),
                "initialized": seal_data.get("initialized", False),
                "sealed": seal_data.get("sealed", False),
                "standby": seal_data.get("standby", False),
                "performance_standby": seal_data.get("performance_standby", False),
                "replication_performance_mode": seal_data.get("replication_performance_mode"),
                "replication_dr_mode": seal_data.get("replication_dr_mode"),
                "server_time_utc": seal_data.get("server_time_utc"),
                "build_date": seal_data.get("build_date"),
                "go_version": seal_data.get("go_version"),
                "warnings": seal_data.get("warnings", [])
            })
            
        except Exception as e:
            self.logger.warning(f"Error reading seal status: {str(e)}")
        
        # Get leader status for additional information
        try:
            leader_response = self.client.sys.read_leader_status()
            leader_data = self._safe_get_data(leader_response)
            
            record.update({
                "leader_address": leader_data.get("leader_address"),
                "leader_cluster_address": leader_data.get("leader_cluster_address"),
                "is_leader": leader_data.get("is_self", False),
                "ha_enabled": leader_data.get("ha_enabled", False)
            })
            
        except Exception as e:
            self.logger.debug(f"Error reading leader status: {str(e)}")
        
        yield record