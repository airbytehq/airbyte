#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, List

from .base import VaultStream


class Secrets(VaultStream):
    """Stream for retrieving secret names from Vault (without values)."""
    
    @property
    def name(self) -> str:
        return "secrets"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "path": {"type": ["string", "null"]},
                "mount_path": {"type": ["string", "null"]},
                "mount_type": {"type": ["string", "null"]},
                "version": {"type": ["integer", "null"]},
                "created_time": {"type": ["string", "null"]},
                "updated_time": {"type": ["string", "null"]},
                "custom_metadata": {"type": ["object", "null"]},
                "namespace": {"type": ["string", "null"]},
            }
        }
    
    def _list_secrets_recursive(self, mount_path: str, path: str = "") -> List[Mapping[str, Any]]:
        """Recursively list all secrets in a mount."""
        secrets = []
        
        try:
            # Build the full path for listing
            full_path = f"{mount_path}{path}"
            
            # List items at current path
            list_response = self.client.list(full_path)
            
            if not list_response or "data" not in list_response:
                return secrets
            
            keys = list_response["data"].get("keys", [])
            
            for key in keys:
                if key.endswith('/'):
                    # This is a directory, recurse into it
                    sub_path = f"{path}{key}"
                    sub_secrets = self._list_secrets_recursive(mount_path, sub_path)
                    secrets.extend(sub_secrets)
                else:
                    # This is a secret
                    secret_path = f"{path}{key}"
                    full_secret_path = f"{mount_path}{secret_path}"
                    
                    secret_record = {
                        "id": full_secret_path,
                        "path": secret_path,
                        "mount_path": mount_path,
                        "mount_type": "kv",  # Will be updated with actual type
                        "version": None,
                        "created_time": None,
                        "updated_time": None,
                        "custom_metadata": {},
                        "namespace": self.namespace,
                    }
                    
                    # Try to get metadata for KV v2 secrets
                    try:
                        metadata_path = f"{mount_path}metadata/{secret_path}"
                        metadata_response = self.client.read(metadata_path)
                        
                        if metadata_response and "data" in metadata_response:
                            metadata = metadata_response["data"]
                            secret_record["version"] = metadata.get("current_version")
                            secret_record["created_time"] = metadata.get("created_time")
                            secret_record["updated_time"] = metadata.get("updated_time")
                            secret_record["custom_metadata"] = metadata.get("custom_metadata", {})
                    except:
                        # Not a KV v2 secret or no access to metadata
                        pass
                    
                    secrets.append(secret_record)
                    
        except Exception as e:
            self.logger.debug(f"Error listing secrets at {mount_path}{path}: {str(e)}")
            
        return secrets
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read secret names from all secret engines."""
        try:
            # List all secret engines
            mounts_response = self.client.sys.list_mounted_secrets_engines()
            
            if not mounts_response or "data" not in mounts_response:
                return
            
            for mount_path, mount_info in mounts_response["data"].items():
                mount_type = mount_info.get("type", "")
                
                # Only process KV and generic secret engines
                if mount_type not in ["kv", "kv-v2", "generic", "cubbyhole"]:
                    continue
                
                # Clean mount path
                if not mount_path.endswith('/'):
                    mount_path += '/'
                
                # List all secrets recursively
                secrets = self._list_secrets_recursive(mount_path)
                
                # Update mount type for all secrets
                for secret in secrets:
                    secret["mount_type"] = mount_type
                    yield secret
                    
        except Exception as e:
            self.logger.error(f"Error listing secret engines: {str(e)}")
            return