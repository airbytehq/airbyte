#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, List
import hvac

from .base import VaultStream


class ServiceAccounts(VaultStream):
    """Stream for retrieving service accounts from Vault's AppRole auth method and identity entities without user-based auth aliases across all namespaces."""
    
    @property
    def name(self) -> str:
        return "service_accounts"
    
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
                "namespace_path": {"type": ["string", "null"]},
                "creation_time": {"type": ["string", "null"]},
                "last_update_time": {"type": ["string", "null"]},
                "disabled": {"type": ["boolean", "null"]},
                "account_source": {"type": ["string", "null"]},
                "auth_method": {"type": ["string", "null"]},
                "mount_path": {"type": ["string", "null"]},
                # AppRole specific fields
                "role_id": {"type": ["string", "null"]},
                "bind_secret_id": {"type": ["boolean", "null"]},
                "secret_id_bound_cidrs": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "secret_id_num_uses": {"type": ["integer", "null"]},
                "secret_id_ttl": {"type": ["integer", "null"]},
                "token_ttl": {"type": ["integer", "null"]},
                "token_max_ttl": {"type": ["integer", "null"]},
                "token_bound_cidrs": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "token_num_uses": {"type": ["integer", "null"]},
                "token_type": {"type": ["string", "null"]},
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
        Each slice represents a namespace to scan for service accounts.
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
    
    def _has_user_auth_aliases(self, entity_data: Mapping[str, Any]) -> bool:
        """
        Check if an identity entity has aliases from user-based auth methods.
        """
        aliases = entity_data.get("aliases", [])
        user_auth_methods = ["userpass", "ldap", "okta", "radius", "oidc", "jwt", "github"]
        
        return any(
            alias.get("mount_type") in user_auth_methods 
            for alias in aliases
        )
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read service accounts from Vault identity store and AppRole auth methods for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for service accounts in namespace: {namespace_path}")
        
        # Create client for this namespace
        client = self._create_client_for_namespace(namespace_path)

        # 1. Scan Identity Entities that DON'T have user-based auth method aliases
        try:
            # List all entities in this namespace
            list_response = client.secrets.identity.list_entities()
            
            if list_response and "data" in list_response:
                key_info = list_response["data"].get("key_info", {})
                entity_ids = list_response["data"].get("keys", [])
                self.logger.debug(f"Found {len(entity_ids)} identity entities in namespace {namespace_path}")
                
                for entity_id in entity_ids:
                    try:
                        # Get basic info from key_info
                        basic_info = key_info.get(entity_id, {})

                        # Try to get full details by name if available
                        entity_data = {}
                        entity_name = basic_info.get("name")
                        if entity_name:
                            try:
                                entity_response = client.secrets.identity.read_entity_by_name(name=entity_name)
                                if entity_response and "data" in entity_response:
                                    entity_data = entity_response["data"]
                            except Exception as e:
                                self.logger.debug(f"Could not read full entity details for {entity_name}: {str(e)}")
                        
                        # Use basic info if full details not available
                        if not entity_data:
                            entity_data = basic_info
                            entity_data["id"] = entity_id
                        
                        # Only include if this entity does NOT have user-based auth method aliases
                        if not self._has_user_auth_aliases(entity_data):
                            record = {
                                "id": entity_data.get("id", entity_id),
                                "name": entity_data.get("name"),
                                "metadata": entity_data.get("metadata", {}),
                                "policies": entity_data.get("policies", []),
                                "aliases": entity_data.get("aliases", []),
                                "group_ids": entity_data.get("group_ids", []),
                                "direct_group_ids": entity_data.get("direct_group_ids", []),
                                "inherited_group_ids": entity_data.get("inherited_group_ids", []),
                                "namespace_id": entity_data.get("namespace_id"),
                                "namespace_path": namespace_path,
                                "creation_time": entity_data.get("creation_time"),
                                "last_update_time": entity_data.get("last_update_time"),
                                "disabled": entity_data.get("disabled"),
                                "account_source": "identity_entity",
                                "auth_method": None,
                                "mount_path": None,
                                # AppRole specific fields (null for identity entities)
                                "role_id": None,
                                "bind_secret_id": None,
                                "secret_id_bound_cidrs": None,
                                "secret_id_num_uses": None,
                                "secret_id_ttl": None,
                                "token_ttl": None,
                                "token_max_ttl": None,
                                "token_bound_cidrs": None,
                                "token_num_uses": None,
                                "token_type": None,
                            }
                            
                            yield record

                    except Exception as e:
                        self.logger.warning(f"Error processing entity {entity_id} in namespace {namespace_path}: {str(e)}")
                        continue
            else:
                self.logger.debug(f"No identity entities found in namespace: {namespace_path}")
                
        except Exception as e:
            self.logger.debug(f"Error listing identity entities in namespace {namespace_path}: {str(e)}")
        
        # 2. Scan AppRole Auth Methods for actual service account roles
        try:
            # List all auth methods
            auth_methods = client.sys.list_auth_methods()
            
            if auth_methods and isinstance(auth_methods, dict) and "data" in auth_methods:
                approle_count = 0
                
                for mount_path, auth_data in auth_methods["data"].items():
                    auth_type = auth_data.get("type", "")
                    
                    # Only process AppRole auth methods
                    if auth_type == "approle":
                        approle_count += 1
                        
                        try:
                            # List all roles in this AppRole mount
                            roles_path = f"auth/{mount_path}role"
                            
                            try:
                                roles_response = client.list(roles_path)
                            except:
                                # Try alternative path
                                roles_path = f"auth/{mount_path}roles"
                                try:
                                    roles_response = client.list(roles_path)
                                except:
                                    self.logger.debug(f"Could not list roles for AppRole mount {mount_path}")
                                    continue
                            
                            if roles_response and isinstance(roles_response, dict) and "data" in roles_response:
                                role_names = roles_response["data"].get("keys", [])
                                self.logger.debug(f"Found {len(role_names)} AppRole roles in {mount_path}")
                                
                                for role_name in role_names:
                                    try:
                                        # Read role details
                                        role_path = f"auth/{mount_path}role/{role_name}"
                                        role_response = client.read(role_path)
                                        
                                        if role_response and isinstance(role_response, dict) and "data" in role_response:
                                            role_data = role_response["data"]
                                            
                                            # Get role ID
                                            role_id_path = f"auth/{mount_path}role/{role_name}/role-id"
                                            try:
                                                role_id_response = client.read(role_id_path)
                                                if role_id_response and isinstance(role_id_response, dict) and "data" in role_id_response:
                                                    role_id = role_id_response["data"]["role_id"]
                                                else:
                                                    role_id = None
                                            except:
                                                role_id = None
                                            
                                            # Create service account record for AppRole
                                            record = {
                                                "id": f"{mount_path}{role_name}",
                                                "name": role_name,
                                                "metadata": {
                                                    "description": role_data.get("description", ""),
                                                    "mount_path": mount_path,
                                                    "mount_type": auth_type,
                                                },
                                                "policies": role_data.get("policies", []) + role_data.get("token_policies", []),
                                                "aliases": [],  # AppRoles don't have aliases like identity entities
                                                "group_ids": [],
                                                "direct_group_ids": [],
                                                "inherited_group_ids": [],
                                                "namespace_id": None,
                                                "namespace_path": namespace_path,
                                                "creation_time": None,  # AppRoles don't have creation timestamps
                                                "last_update_time": None,
                                                "disabled": False,
                                                "account_source": "approle",
                                                "auth_method": auth_type,
                                                "mount_path": mount_path,
                                                # AppRole specific fields
                                                "role_id": role_id,
                                                "bind_secret_id": role_data.get("bind_secret_id", True),
                                                "secret_id_bound_cidrs": role_data.get("secret_id_bound_cidrs", []),
                                                "secret_id_num_uses": role_data.get("secret_id_num_uses"),
                                                "secret_id_ttl": role_data.get("secret_id_ttl"),
                                                "token_ttl": role_data.get("token_ttl"),
                                                "token_max_ttl": role_data.get("token_max_ttl"),
                                                "token_bound_cidrs": role_data.get("token_bound_cidrs", []),
                                                "token_num_uses": role_data.get("token_num_uses"),
                                                "token_type": role_data.get("token_type"),
                                            }
                                            
                                            yield record
                                            
                                    except Exception as e:
                                        self.logger.warning(f"Error reading AppRole {role_name} from {mount_path} in namespace {namespace_path}: {str(e)}")
                                        continue
                                        
                        except Exception as e:
                            self.logger.debug(f"Could not list roles for AppRole mount {mount_path} in namespace {namespace_path}: {str(e)}")
                            continue
                
                self.logger.debug(f"Processed {approle_count} AppRole auth methods in namespace {namespace_path}")
            else:
                self.logger.debug(f"No auth methods found in namespace: {namespace_path}")
                
        except Exception as e:
            self.logger.debug(f"Error listing auth methods in namespace {namespace_path}: {str(e)}") 