from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream
from .domains import Domains
from .forest import Forest


class ForestDomains(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "forest_domains"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Unique relationship identifier"},
                "forest_id": {"type": ["string"], "description": "Forest's unique objectGUID identifier"},
                "forest_name": {"type": ["string"], "description": "Forest DNS name"},
                "domain_id": {"type": ["string"], "description": "Domain's unique objectGUID identifier"},
                "domain_name": {"type": ["string"], "description": "Domain DNS name"},
                "domain_distinguished_name": {"type": ["string"], "description": "Domain distinguished name"},
                "is_root_domain": {"type": ["boolean"], "description": "Whether this is the forest root domain"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read forest to domain relationships from Active Directory."""
        
        try:
            # Get forest information using the existing forest stream
            forest_stream = Forest(conn=self._conn)
            forest_records = list(forest_stream.read_records(sync_mode))
            
            if not forest_records:
                return
            
            forest_info = forest_records[0]  # Forest stream typically returns one record
            
            # Get all domains using the existing domains stream
            domains_stream = Domains(conn=self._conn)
            
            # Create relationship records
            for domain in domains_stream.read_records(sync_mode):
                try:
                    relationship_id = f"{forest_info['id']}_{domain['id']}"
                    
                    forest_domain_record = {
                        "id": relationship_id,
                        "forest_id": forest_info["id"],
                        "forest_name": forest_info["name"],
                        "domain_id": domain["id"],
                        "domain_name": domain["name"],
                        "domain_distinguished_name": domain["distinguished_name"],
                        "is_root_domain": domain["name"] == forest_info.get("root_domain"),
                    }
                    
                    yield forest_domain_record
                    
                except Exception as e:
                    self.logger.warning(f"Error processing forest-domain relationship: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during forest-domains search: {str(e)}")
            raise
