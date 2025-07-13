#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping, Optional, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin

from .base import VaultStream


class Audit(VaultStream, IncrementalMixin):
    """Stream for retrieving audit logs from Vault."""
    
    # This stream supports incremental sync
    _cursor_field = "timestamp"
    
    @property
    def name(self) -> str:
        return "audit"
    
    @property
    def primary_key(self) -> Optional[str]:
        return None  # Audit logs don't have a unique ID
    
    @property
    def cursor_field(self) -> str:
        """The field used for incremental sync."""
        return self._cursor_field
    
    @property
    def source_defined_cursor(self) -> bool:
        """Whether the cursor field is defined by the source."""
        return True
    
    @property
    def supports_incremental(self) -> bool:
        """Whether this stream supports incremental sync."""
        return True
    
    @property
    def supported_sync_modes(self) -> List[SyncMode]:
        """List of sync modes supported by this stream."""
        return [SyncMode.full_refresh, SyncMode.incremental]
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "timestamp": {"type": ["string", "null"], "format": "date-time"},
                "type": {"type": ["string", "null"]},
                "auth": {
                    "type": ["object", "null"],
                    "properties": {
                        "accessor": {"type": ["string", "null"]},
                        "client_token": {"type": ["string", "null"]},
                        "display_name": {"type": ["string", "null"]},
                        "entity_id": {"type": ["string", "null"]},
                        "metadata": {"type": ["object", "null"]},
                        "policies": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                        "token_type": {"type": ["string", "null"]},
                    }
                },
                "request": {
                    "type": ["object", "null"],
                    "properties": {
                        "id": {"type": ["string", "null"]},
                        "operation": {"type": ["string", "null"]},
                        "client_token": {"type": ["string", "null"]},
                        "path": {"type": ["string", "null"]},
                        "data": {"type": ["object", "null"]},
                        "remote_address": {"type": ["string", "null"]},
                        "headers": {"type": ["object", "null"]},
                    }
                },
                "response": {
                    "type": ["object", "null"],
                    "properties": {
                        "data": {"type": ["object", "null"]},
                        "redirect": {"type": ["string", "null"]},
                        "warnings": {
                            "type": ["array", "null"],
                            "items": {"type": "string"}
                        },
                    }
                },
                "error": {"type": ["string", "null"]},
                "audit_device": {
                    "type": ["object", "null"],
                    "properties": {
                        "path": {"type": ["string", "null"]},
                        "type": {"type": ["string", "null"]},
                        "description": {"type": ["string", "null"]},
                    }
                },
                "namespace": {"type": ["string", "null"]},
            },
            "required": ["timestamp"]
        }
    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """Update the stream state with the latest record's cursor value."""
        current_timestamp = current_stream_state.get(self.cursor_field, "")
        latest_timestamp = latest_record.get(self.cursor_field, "")
        
        if latest_timestamp > current_timestamp:
            current_stream_state[self.cursor_field] = latest_timestamp
            
        return current_stream_state
    
    def _parse_audit_log_line(self, line: str) -> Optional[Mapping[str, Any]]:
        """Parse a single audit log line (usually JSON formatted)."""
        try:
            import json
            log_entry = json.loads(line)
            
            # Ensure timestamp is present and properly formatted
            if "time" in log_entry:
                # Convert Vault timestamp to ISO format
                timestamp = log_entry["time"]
                if isinstance(timestamp, str):
                    # Already a string, ensure it's ISO formatted
                    try:
                        # Try to parse and reformat
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.isoformat()
                    except:
                        # If parsing fails, use current time
                        timestamp = datetime.now(timezone.utc).isoformat()
                else:
                    # If it's not a string, use current time
                    timestamp = datetime.now(timezone.utc).isoformat()
            else:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            # Transform Vault audit log format to our schema
            record = {
                "timestamp": timestamp,
                "type": log_entry.get("type"),
                "auth": log_entry.get("auth", {}),
                "request": log_entry.get("request", {}),
                "response": log_entry.get("response", {}),
                "error": log_entry.get("error"),
                "namespace": self.namespace,
            }
            
            return record
            
        except Exception as e:
            self.logger.warning(f"Failed to parse audit log line: {str(e)}")
            return None
    
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read audit logs from Vault."""
        # Get the cursor value for incremental sync
        cursor_value = None
        if sync_mode == SyncMode.incremental and stream_state:
            cursor_value = stream_state.get(self.cursor_field)
        
        try:
            # First, list all audit devices
            audit_devices = self.client.sys.list_enabled_audit_devices()
            
            if not audit_devices or "data" not in audit_devices:
                self.logger.info("No audit devices configured")
                return
            
            # Return information about configured audit devices
            for device_path, device_info in audit_devices["data"].items():
                audit_device_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "audit_device_info",
                    "auth": {},
                    "request": {
                        "operation": "list",
                        "path": f"sys/audit/{device_path}",
                    },
                    "response": {
                        "data": {
                            "path": device_path,
                            "type": device_info.get("type"),
                            "description": device_info.get("description"),
                            "options": device_info.get("options", {}),
                        }
                    },
                    "error": None,
                    "audit_device": {
                        "path": device_path,
                        "type": device_info.get("type"),
                        "description": device_info.get("description"),
                    },
                    "namespace": self.namespace,
                }
                
                # Skip if this record is before our cursor
                if cursor_value and audit_device_record["timestamp"] <= cursor_value:
                    continue
                    
                yield audit_device_record
            
            # Note: Actual audit logs are typically written to files, syslog, or sockets
            # and are not directly accessible via Vault API. The above code returns
            # information about configured audit devices.
            
            # In a production environment, you would need to:
            # 1. Configure Vault to write audit logs to a location accessible by this connector
            # 2. Read from that location (file, database, etc.)
            # 3. Parse and filter logs based on the cursor_value for incremental sync
            
            # Example placeholder for reading from a file-based audit device:
            """
            audit_log_path = "/var/log/vault/audit.log"
            if os.path.exists(audit_log_path):
                with open(audit_log_path, 'r') as f:
                    for line in f:
                        record = self._parse_audit_log_line(line)
                        if record:
                            # Check cursor for incremental sync
                            if cursor_value and record["timestamp"] <= cursor_value:
                                continue
                            yield record
            """
            
        except Exception as e:
            self.logger.error(f"Error reading audit information: {str(e)}")
            # Return a single error record
            yield {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "error",
                "auth": {},
                "request": {"operation": "list", "path": "sys/audit"},
                "response": {},
                "error": str(e),
                "audit_device": {},
                "namespace": self.namespace,
            }