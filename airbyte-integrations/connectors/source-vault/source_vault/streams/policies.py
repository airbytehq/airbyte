#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional

from .base import VaultStream


class Policies(VaultStream):
    """Stream for retrieving policies from Vault."""
    
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
        """Read policies from Vault."""
        try:
            # List all policies
            policies_response = self.client.sys.list_policies()
            
            if not policies_response or "data" not in policies_response:
                return
                
            policy_names = policies_response["data"].get("keys", [])
            
            for policy_name in policy_names:
                try:
                    # Read policy details
                    policy_response = self.client.sys.read_policy(policy_name)
                    
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
                            "namespace": self.namespace,
                        }
                        
                        yield record
                        
                except Exception as e:
                    self.logger.warning(f"Error reading policy {policy_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error listing policies: {str(e)}")
            return