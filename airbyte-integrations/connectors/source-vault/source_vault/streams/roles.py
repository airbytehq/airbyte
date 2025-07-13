#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class Roles(VaultStream):
    """Stream for retrieving roles from various auth methods in Vault."""
    
    @property
    def name(self) -> str:
        return "roles"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "auth_method": {"type": ["string", "null"]},
                "mount_path": {"type": ["string", "null"]},
                "policies": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "token_policies": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "token_ttl": {"type": ["integer", "null"]},
                "token_max_ttl": {"type": ["integer", "null"]},
                "token_period": {"type": ["integer", "null"]},
                "token_bound_cidrs": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "metadata": {"type": ["object", "null"]},
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
        """Read roles from various auth methods."""
        try:
            # List all auth methods
            auth_methods = self.client.sys.list_auth_methods()
            
            if not auth_methods or "data" not in auth_methods:
                return
                
            for mount_path, auth_data in auth_methods["data"].items():
                auth_type = auth_data.get("type", "")
                
                # Skip non-role based auth methods
                if auth_type in ["token", "cert"]:
                    continue
                
                try:
                    # Try to list roles for this auth method
                    roles_path = f"auth/{mount_path}roles"
                    
                    try:
                        roles_response = self.client.list(roles_path)
                    except:
                        # Some auth methods might use different paths
                        roles_path = f"auth/{mount_path}role"
                        try:
                            roles_response = self.client.list(roles_path)
                        except:
                            continue
                    
                    if roles_response and "data" in roles_response:
                        role_names = roles_response["data"].get("keys", [])
                        
                        for role_name in role_names:
                            try:
                                # Read role details
                                role_path = f"{roles_path}/{role_name}"
                                role_response = self.client.read(role_path)
                                
                                if role_response and "data" in role_response:
                                    role_data = role_response["data"]
                                    
                                    # Create role record
                                    record = {
                                        "id": f"{mount_path}{role_name}",
                                        "name": role_name,
                                        "auth_method": auth_type,
                                        "mount_path": mount_path,
                                        "policies": role_data.get("policies", []),
                                        "token_policies": role_data.get("token_policies", []),
                                        "token_ttl": role_data.get("token_ttl", 0),
                                        "token_max_ttl": role_data.get("token_max_ttl", 0),
                                        "token_period": role_data.get("token_period", 0),
                                        "token_bound_cidrs": role_data.get("token_bound_cidrs", []),
                                        "metadata": {
                                            k: v for k, v in role_data.items() 
                                            if k not in ["policies", "token_policies", "token_ttl", 
                                                       "token_max_ttl", "token_period", "token_bound_cidrs"]
                                        },
                                        "namespace": self.namespace,
                                    }
                                    
                                    yield record
                                    
                            except Exception as e:
                                self.logger.warning(f"Error reading role {role_name} from {mount_path}: {str(e)}")
                                continue
                                
                except Exception as e:
                    self.logger.debug(f"Could not list roles for auth method {mount_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error listing auth methods: {str(e)}")
            return