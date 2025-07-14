#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional
import hvac

from .base import VaultStream


class Policies(VaultStream):
    """Stream for retrieving policies from Vault across all namespaces."""
    
    @property
    def name(self) -> str:
        return "policies"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "rules": {"type": ["string", "null"]},
                "paths": {
                    "type": ["object", "null"],
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "capabilities": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
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
        Each slice represents a namespace to scan for policies.
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
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read policies from Vault for a specific namespace slice."""
        
        # Get namespace from slice, fallback to default
        if stream_slice:
            namespace_path = stream_slice["namespace_path"]
        else:
            namespace_path = self.vault_namespace or "root"
        
        self.logger.info(f"Scanning for policies in namespace: {namespace_path}")
        
        try:
            # Create client for this namespace
            client = self._create_client_for_namespace(namespace_path)
            
            # List all policies
            policies_response = client.sys.list_policies()
            
            if not policies_response or "data" not in policies_response:
                self.logger.debug(f"No policies found in namespace: {namespace_path}")
                return
                
            policy_names = policies_response["data"].get("keys", [])
            self.logger.debug(f"Found {len(policy_names)} policies in namespace {namespace_path}")
            
            for policy_name in policy_names:
                try:
                    # Read policy details
                    policy_response = client.sys.read_policy(policy_name)
                    
                    if policy_response and "data" in policy_response:
                        policy_data = policy_response["data"]
                        
                        # Parse policy rules if possible
                        rules = policy_data.get("rules", "")
                        paths = {}
                        
                        # Try to parse HCL policy to extract paths
                        # This is a simplified parser - real HCL parsing would be more complex
                        if rules:
                            lines = rules.split('\n')
                            current_path = None
                            
                            for line in lines:
                                line = line.strip()
                                if line.startswith('path "') and line.endswith('" {'):
                                    current_path = line[6:-3]  # Extract path
                                    paths[current_path] = {"capabilities": []}
                                elif line.startswith('capabilities = [') and current_path:
                                    # Extract capabilities
                                    caps_str = line[16:]
                                    if caps_str.endswith(']'):
                                        caps_str = caps_str[:-1]
                                    capabilities = [
                                        cap.strip().strip('"') 
                                        for cap in caps_str.split(',')
                                        if cap.strip()
                                    ]
                                    paths[current_path]["capabilities"] = capabilities
                        
                        record = {
                            "id": policy_name,
                            "name": policy_name,
                            "rules": rules,
                            "paths": paths,
                            "namespace_path": namespace_path,
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading policy {policy_name} in namespace {namespace_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error listing policies in namespace {namespace_path}: {str(e)}")
            return