#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, List
import hvac

from .base import VaultStream


class Secrets(VaultStream):
    """Stream for retrieving secret names from Vault (without values) across all namespaces."""
    
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
        Each slice represents a namespace to scan for secrets.
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
    
    def _list_secrets_recursive(self, client: hvac.Client, mount_path: str, list_prefix: str, is_kv_v2: bool, mount_type: str, path: str = "") -> List[Mapping[str, Any]]:
        """Recursively list all secrets in a mount using the given prefix."""
        secrets = []
        
        try:
            # Build the full path for listing
            full_path = f"{mount_path}{list_prefix}{path}"
            
            # List items at current path
            list_response = client.list(full_path)
            
            if not list_response or not isinstance(list_response, dict) or "data" not in list_response:
                return secrets
            
            keys = list_response["data"].get("keys", [])
            
            for key in keys:
                if key.endswith('/'):
                    # This is a directory, recurse into it
                    sub_path = f"{path}{key}"
                    sub_secrets = self._list_secrets_recursive(client, mount_path, list_prefix, is_kv_v2, mount_type, sub_path)
                    secrets.extend(sub_secrets)
                else:
                    # This is a secret
                    secret_path = f"{path}{key}"
                    full_secret_id = f"{mount_path}{secret_path}"
                    
                    secret_record = {
                        "id": full_secret_id,
                        "path": secret_path,
                        "mount_path": mount_path,
                        "mount_type": mount_type,
                        "version": None,
                        "created_time": None,
                        "updated_time": None,
                        "custom_metadata": {},
                        "namespace_path": None,  # Will be set by caller
                    }
                    
                    # Try to get metadata if KV v2
                    if is_kv_v2:
                        try:
                            metadata_path = f"{mount_path}metadata/{secret_path}"
                            metadata_response = client.read(metadata_path)
                            
                            if metadata_response and isinstance(metadata_response, dict) and "data" in metadata_response:
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
            self.logger.debug(f"Error listing secrets at {full_path}: {str(e)}")
            
        return secrets
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read secret names from all secret engines for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for secrets in namespace: {namespace_path}")
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(namespace_path)
            
            # List all secret engines
            mounts_response = client.sys.list_mounted_secrets_engines()
            
            if not mounts_response or "data" not in mounts_response:
                self.logger.debug(f"No secret engines found in namespace: {namespace_path}")
                return
            
            mount_count = 0
            skipped_count = 0
            for mount_path, mount_info in mounts_response["data"].items():
                mount_type = mount_info.get("type", "")
                options = mount_info.get("options", {})
                engine_version = options.get("version") if options else None
                
                is_kv_v2 = (mount_type == "kv" and engine_version == "2")
                
                mount_count += 1
                
                # Clean mount path
                if not mount_path.endswith('/'):
                    mount_path += '/'
                
                # Determine prefix for listing metadata (only for KV v2)
                list_prefix = "metadata/" if is_kv_v2 else ""
                
                self.logger.debug(f"Attempting to scan mount: {mount_path} (type: {mount_type})")
                
                try:
                    # List all secrets recursively
                    secrets = self._list_secrets_recursive(
                        client=client,
                        mount_path=mount_path,
                        list_prefix=list_prefix,
                        is_kv_v2=is_kv_v2,
                        mount_type=mount_type
                    )
                    
                    if not secrets:
                        self.logger.debug(f"No secrets found in mount: {mount_path}")
                    
                    # Update mount type and namespace for all secrets
                    for secret in secrets:
                        updated_secret = dict(secret)
                        updated_secret["mount_type"] = mount_type
                        updated_secret["namespace_path"] = namespace_path
                        yield updated_secret
                except Exception as e:
                    skipped_count += 1
                    self.logger.debug(f"Skipping mount {mount_path} (type: {mount_type}): {str(e)}")
            
            self.logger.debug(f"Processed {mount_count} secret engines (skipped {skipped_count}) in namespace {namespace_path}")
                    
        except Exception as e:
            self.logger.debug(f"Error listing secret engines in namespace {namespace_path}: {str(e)}")
            return