from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream
from .domains import Domains


class OrganizationalUnits(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "organizational_units"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "OU's unique objectGUID identifier"},
                "name": {"type": ["string"], "description": "OU name"},
                "distinguished_name": {"type": ["string"], "description": "OU distinguished name"},
                "description": {"type": ["string", "null"], "description": "OU description"},
                "canonical_name": {"type": ["string", "null"], "description": "OU canonical name"},
                "parent_ou_id": {"type": ["string", "null"], "description": "Parent OU's objectGUID (if any)"},
                "domain_id": {"type": ["string", "null"], "description": "Domain objectGUID this OU belongs to"},
                "created_at": {"type": ["string", "null"], "description": "OU creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Last modification time"},
                "gpo_links": {"type": ["array"], "items": {"type": "string"}, "description": "Group Policy Object links"},
                "managed_by": {"type": ["string", "null"], "description": "Distinguished name of managing object"},
                "street_address": {"type": ["string", "null"], "description": "Street address"},
                "city": {"type": ["string", "null"], "description": "City/locality"},
                "state": {"type": ["string", "null"], "description": "State/province"},
                "postal_code": {"type": ["string", "null"], "description": "Postal code"},
                "country": {"type": ["string", "null"], "description": "Country"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read Organizational Units from Active Directory."""
        
        try:
            # Get all domains using the existing domains stream
            domains_stream = Domains(conn=self._conn)
            
            for domain in domains_stream.read_records(sync_mode):
                try:
                    domain_context = domain['distinguished_name']
                    domain_id = domain['id']
                    
                    # Search for organizational unit objects
                    search_filter = "(objectClass=organizationalUnit)"
                    
                    attributes = [
                        'objectGUID',
                        'name',
                        'distinguishedName',
                        'description',
                        'canonicalName',
                        'whenCreated',
                        'whenChanged',
                        'gPLink',
                        'managedBy',
                        'street',
                        'l',  # city/locality
                        'st', # state/province
                        'postalCode',
                        'c',  # country
                    ]
                    
                    success = self._conn.search(
                        search_base=domain_context,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=attributes
                    )
                    
                    if not success:
                        self.logger.warning(f"Failed to search for OUs in domain {domain_context}: {self._conn.result}")
                        continue
                    
                    for entry in self._conn.entries:
                        try:
                            object_guid = entry.objectGUID
                            if not object_guid:
                                continue
                            
                            # Parse distinguished name to find parent OU
                            parent_ou_id = self._get_parent_ou_id(str(entry.distinguishedName.value))
                            
                            # Parse GPO links
                            gpo_links = self._parse_gpo_links(entry.gPLink.value if hasattr(entry, 'gPLink') and entry.gPLink else None)
                            
                            ou_record = {
                                "id": self._strip_guid_parents(object_guid.value),
                                "name": str(entry.name.value) if hasattr(entry, 'name') and entry.name else None,
                                "distinguished_name": str(entry.distinguishedName.value) if hasattr(entry, 'distinguishedName') and entry.distinguishedName else None,
                                "description": str(entry.description.value) if hasattr(entry, 'description') and entry.description else None,
                                "canonical_name": str(entry.canonicalName.value) if hasattr(entry, 'canonicalName') and entry.canonicalName else None,
                                "parent_ou_id": parent_ou_id,
                                "domain_id": domain_id,
                                "created_at": str(entry.whenCreated.value) if hasattr(entry, 'whenCreated') and entry.whenCreated else None,
                                "modified_at": str(entry.whenChanged.value) if hasattr(entry, 'whenChanged') and entry.whenChanged else None,
                                "gpo_links": gpo_links,
                                "managed_by": str(entry.managedBy.value) if hasattr(entry, 'managedBy') and entry.managedBy else None,
                                "street_address": str(entry.street.value) if hasattr(entry, 'street') and entry.street else None,
                                "city": str(entry.l.value) if hasattr(entry, 'l') and entry.l else None,
                                "state": str(entry.st.value) if hasattr(entry, 'st') and entry.st else None,
                                "postal_code": str(entry.postalCode.value) if hasattr(entry, 'postalCode') and entry.postalCode else None,
                                "country": str(entry.c.value) if hasattr(entry, 'c') and entry.c else None,
                            }
                            
                            yield ou_record
                            
                        except Exception as e:
                            self.logger.warning(f"Error processing OU entry {entry.entry_dn}: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error searching domain context {domain_context}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during organizational units search: {str(e)}")
            raise
    
    def _get_parent_ou_id(self, distinguished_name: str) -> Optional[str]:
        """Extract parent OU ID from distinguished name."""
        try:
            # Parse DN to find parent OU
            dn_parts = distinguished_name.split(',')
            if len(dn_parts) > 1:
                parent_dn = ','.join(dn_parts[1:])
                
                # Check if parent is an OU
                if parent_dn.startswith('OU='):
                    # Search for the parent OU to get its objectGUID
                    success = self._conn.search(
                        search_base=parent_dn,
                        search_filter="(objectClass=organizationalUnit)",
                        search_scope=SUBTREE,
                        attributes=['objectGUID']
                    )
                    
                    if success and self._conn.entries:
                        for entry in self._conn.entries:
                            if hasattr(entry, 'objectGUID') and entry.objectGUID:
                                return self._strip_guid_parents(entry.objectGUID.value)
            return None
        except Exception:
            return None
    
    def _parse_gpo_links(self, gp_link: str) -> list:
        """Parse Group Policy Object links."""
        if not gp_link:
            return []
        
        try:
            # GPO links are stored as [LDAP://CN=GUID,CN=Policies,CN=System,DC=...;OPTIONS]
            gpo_links = []
            parts = gp_link.split('[')
            for part in parts[1:]:  # Skip first empty part
                if ';' in part:
                    gpo_dn = part.split(';')[0]
                    if gpo_dn.startswith('LDAP://'):
                        gpo_dn = gpo_dn[7:]  # Remove LDAP:// prefix
                    gpo_links.append(gpo_dn)
            return gpo_links
        except Exception:
            return []
