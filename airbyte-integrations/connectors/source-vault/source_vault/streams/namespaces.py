#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, List

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
    
    def _list_namespaces_recursive(self, parent_path: str = "") -> List[Mapping[str, Any]]:
        """Recursively list all namespaces."""
        namespaces = []
        
        try:
            # List namespaces at current level
            if parent_path:
                # Set the namespace context for listing
                original_namespace = self.client.namespace
                self.client.namespace = parent_path
                
            list_response = self.client.sys.list_namespaces()
            
            if parent_path:
                # Restore original namespace
                self.client.namespace = original_namespace
            
            if list_response and "data" in list_response:
                namespace_names = list_response["data"].get("keys", [])
                
                for ns_name in namespace_names:
                    # Clean namespace name (remove trailing slash)
                    ns_name = ns_name.rstrip('/')
                    
                    # Build full path
                    if parent_path:
                        full_path = f"{parent_path}/{ns_name}"
                    else:
                        full_path = ns_name
                    
                    # Add this namespace
                    namespace_record = {
                        "id": full_path,
                        "path": full_path,
                        "parent_namespace": parent_path or None,
                        "custom_metadata": {},
                    }
                    
                    # Try to get additional metadata
                    try:
                        if parent_path:
                            self.client.namespace = parent_path
                            
                        ns_detail = self.client.read(f"sys/namespaces/{ns_name}")
                        
                        if parent_path:
                            self.client.namespace = original_namespace
                            
                        if ns_detail and "data" in ns_detail:
                            namespace_record["custom_metadata"] = ns_detail["data"].get("custom_metadata", {})
                    except:
                        pass
                    
                    namespaces.append(namespace_record)
                    
                    # Recursively list child namespaces
                    child_namespaces = self._list_namespaces_recursive(full_path)
                    namespaces.extend(child_namespaces)
                    
        except Exception as e:
            self.logger.debug(f"Error listing namespaces at {parent_path}: {str(e)}")
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
        current_namespace = self.namespace or "root"
        yield {
            "id": current_namespace,
            "path": current_namespace,
            "parent_namespace": None,
            "custom_metadata": {},
        }
        
        # List all child namespaces recursively
        namespaces = self._list_namespaces_recursive(self.namespace)
        
        for namespace in namespaces:
            yield namespace