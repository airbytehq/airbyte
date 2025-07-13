#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class VaultInfo(VaultStream):
    """Stream for retrieving information about the Vault instance."""
    
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
                "cluster_id": {"type": ["string", "null"]},
                "cluster_name": {"type": ["string", "null"]},
                "version": {"type": ["string", "null"]},
                "is_self_hosted": {"type": ["boolean", "null"]},
                "initialized": {"type": ["boolean", "null"]},
                "sealed": {"type": ["boolean", "null"]},
                "standby": {"type": ["boolean", "null"]},
                "performance_standby": {"type": ["boolean", "null"]},
                "replication_performance_mode": {"type": ["string", "null"]},
                "replication_dr_mode": {"type": ["string", "null"]},
                "server_time_utc": {"type": ["string", "null"]},
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
        """Read Vault system information."""
        try:
            # Get health status
            health = self.client.sys.read_health_status(method="GET")
            
            # Get seal status
            seal_status = self.client.sys.read_seal_status()
            
            # Get version info
            try:
                version_info = self.client.sys.read_leader_status()
            except:
                version_info = {}
            
            record = {
                "cluster_id": health.get("cluster_id"),
                "cluster_name": health.get("cluster_name"),
                "version": health.get("version"),
                "is_self_hosted": not health.get("enterprise", False),
                "initialized": seal_status.get("initialized", False),
                "sealed": seal_status.get("sealed", False),
                "standby": health.get("standby", False),
                "performance_standby": health.get("performance_standby", False),
                "replication_performance_mode": health.get("replication_performance_mode"),
                "replication_dr_mode": health.get("replication_dr_mode"),
                "server_time_utc": health.get("server_time_utc"),
                "namespace": self.namespace or "root",
            }
            
            yield record
            
        except Exception as e:
            self.logger.error(f"Error reading vault info: {str(e)}")
            # Return minimal info if we can't get full details
            yield {
                "namespace": self.namespace or "root",
                "error": str(e)
            }