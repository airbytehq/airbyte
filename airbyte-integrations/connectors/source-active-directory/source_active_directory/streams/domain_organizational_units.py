from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream
from .domains import Domains


class DomainOrganizationalUnits(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "domain_organizational_units"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Unique relationship identifier"},
                "domain_id": {"type": ["string"], "description": "Domain's unique objectGUID identifier"},
                "domain_name": {"type": ["string"], "description": "Domain DNS name"},
                "domain_distinguished_name": {"type": ["string"], "description": "Domain distinguished name"},
                "ou_id": {"type": ["string"], "description": "OU's unique objectGUID identifier"},
                "ou_name": {"type": ["string"], "description": "OU name"},
                "ou_distinguished_name": {"type": ["string"], "description": "OU distinguished name"},
                "is_direct_child": {"type": ["boolean"], "description": "Whether the OU is a direct child of the domain"},
                "ou_level": {"type": ["integer"], "description": "Depth level of OU within domain (0 = direct child)"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read domain to organizational unit relationships from Active Directory."""
        
        try:
            # Get domains using the existing domains stream
            domains_stream = Domains(conn=self._conn)
            
            for domain in domains_stream.read_records(sync_mode):
                try:
                    # Search for organizational units in this domain
                    ous = self._get_domain_ous(domain['distinguished_name'])
                    
                    for ou in ous:
                        try:
                            relationship_id = f"{domain['id']}_{ou['id']}"
                            
                            # Calculate OU level and check if direct child
                            ou_level = self._calculate_ou_level(ou['distinguished_name'], domain['distinguished_name'])
                            is_direct_child = ou_level == 0
                            
                            domain_ou_record = {
                                "id": relationship_id,
                                "domain_id": domain["id"],
                                "domain_name": domain["name"],
                                "domain_distinguished_name": domain["distinguished_name"],
                                "ou_id": ou["id"],
                                "ou_name": ou["name"],
                                "ou_distinguished_name": ou["distinguished_name"],
                                "is_direct_child": is_direct_child,
                                "ou_level": ou_level,
                            }
                            
                            yield domain_ou_record
                            
                        except Exception as e:
                            self.logger.warning(f"Error processing domain-OU relationship: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error processing domain {domain['name']}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during domain-organizational units search: {str(e)}")
            raise
    
    def _get_domain_ous(self, domain_context: str) -> list:
        """Get all organizational units in a specific domain."""
        try:
            search_filter = "(objectClass=organizationalUnit)"
            
            success = self._conn.search(
                search_base=domain_context,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['objectGUID', 'name', 'distinguishedName']
            )
            
            ous = []
            if success:
                for entry in self._conn.entries:
                    try:
                        if hasattr(entry, 'objectGUID') and entry.objectGUID:
                            ou = {
                                "id": self._strip_guid_parents(entry.objectGUID.value),
                                "name": str(entry.name.value) if hasattr(entry, 'name') and entry.name else None,
                                "distinguished_name": str(entry.distinguishedName.value) if hasattr(entry, 'distinguishedName') and entry.distinguishedName else None,
                            }
                            ous.append(ou)
                    except Exception as e:
                        self.logger.warning(f"Error processing OU entry: {str(e)}")
                        continue
            return ous
        except Exception:
            return []
    
    def _calculate_ou_level(self, ou_dn: str, domain_dn: str) -> int:
        """Calculate the depth level of an OU within the domain."""
        try:
            # Remove the domain DN from the OU DN
            ou_relative_dn = ou_dn.replace(f",{domain_dn}", "")
            
            # Count the number of OU= components
            ou_components = [part.strip() for part in ou_relative_dn.split(',') if part.strip().startswith('OU=')]
            
            # Level is the number of OU components minus 1 (since we want 0-based indexing for direct children)
            return max(0, len(ou_components) - 1)
        except Exception:
            return 0
