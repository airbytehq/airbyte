from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Domains(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "domains"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Domain's unique objectGUID identifier"},
                "name": {"type": ["string"], "description": "Domain name (DNS name)"},
                "netbios_name": {"type": ["string", "null"], "description": "NetBIOS domain name"},
                "distinguished_name": {"type": ["string"], "description": "Domain distinguished name"},
                "functional_level": {"type": ["string", "null"], "description": "Domain functional level"},
                "forest_name": {"type": ["string", "null"], "description": "Forest DNS name"},
                "created_at": {"type": ["string", "null"], "description": "Domain creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Last modification time"},
                "domain_controllers": {"type": ["array"], "items": {"type": "string"}, "description": "Domain controller object IDs"},
                "trust_relationships": {"type": ["array"], "items": {"type": "object"}, "description": "Trust relationships"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read domains from Active Directory forest."""
        
        try:
            # Get the configuration naming context to find domains
            config_context = self._conn.server.info.other.get('configurationNamingContext', [''])[0]
            
            # Search for domain partitions in the configuration
            search_base = f"CN=Partitions,{config_context}"
            search_filter = "(&(objectClass=crossRef)(systemFlags:1.2.840.113556.1.4.803:=2))"
            
            attributes = [
                'objectGUID',
                'cn',
                'dnsRoot',
                'nETBIOSName',
                'nCName',
                'whenCreated',
                'whenChanged'
            ]
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            if not success:
                self.logger.error(f"Failed to search for domains: {self._conn.result}")
                return
            
            for entry in self._conn.entries:
                try:
                    object_guid = entry.objectGUID
                    if not object_guid:
                        continue
                    
                    domain_dn = str(entry.nCName.value) if hasattr(entry, 'nCName') and entry.nCName else None
                    domain_name = str(entry.dnsRoot.value) if hasattr(entry, 'dnsRoot') and entry.dnsRoot else None
                    
                    # Get domain controllers for this domain
                    domain_controllers = self._get_domain_controllers(domain_dn) if domain_dn else []
                    
                    # Get trust relationships
                    trust_relationships = self._get_trust_relationships(domain_dn) if domain_dn else []
                    
                    domain_record = {
                        "id": self._strip_guid_parents(object_guid.value),
                        "name": domain_name,
                        "netbios_name": str(entry.nETBIOSName.value) if hasattr(entry, 'nETBIOSName') and entry.nETBIOSName else None,
                        "distinguished_name": domain_dn,
                        "functional_level": self._get_domain_functional_level(domain_dn),
                        "forest_name": self._get_forest_name(),
                        "created_at": str(entry.whenCreated.value) if hasattr(entry, 'whenCreated') and entry.whenCreated else None,
                        "modified_at": str(entry.whenChanged.value) if hasattr(entry, 'whenChanged') and entry.whenChanged else None,
                        "domain_controllers": domain_controllers,
                        "trust_relationships": trust_relationships,
                    }
                    
                    yield domain_record
                    
                except Exception as e:
                    self.logger.warning(f"Error processing domain entry {entry.entry_dn}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during domain search: {str(e)}")
            raise
    
    def _get_domain_controllers(self, domain_dn: str) -> list:
        """Get domain controllers for a specific domain."""
        try:
            search_base = f"OU=Domain Controllers,{domain_dn}"
            search_filter = "(objectClass=computer)"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['objectGUID']
            )
            
            if success:
                return [self._strip_guid_parents(entry.objectGUID.value) 
                       for entry in self._conn.entries 
                       if hasattr(entry, 'objectGUID') and entry.objectGUID]
            return []
        except:
            return []
    
    def _get_trust_relationships(self, domain_dn: str) -> list:
        """Get trust relationships for a domain."""
        try:
            search_base = f"CN=System,{domain_dn}"
            search_filter = "(objectClass=trustedDomain)"
            
            attributes = ['trustPartner', 'trustDirection', 'trustType', 'trustAttributes']
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            trusts = []
            if success:
                for entry in self._conn.entries:
                    trust = {
                        "partner": str(entry.trustPartner.value) if hasattr(entry, 'trustPartner') and entry.trustPartner else None,
                        "direction": str(entry.trustDirection.value) if hasattr(entry, 'trustDirection') and entry.trustDirection else None,
                        "type": str(entry.trustType.value) if hasattr(entry, 'trustType') and entry.trustType else None,
                        "attributes": str(entry.trustAttributes.value) if hasattr(entry, 'trustAttributes') and entry.trustAttributes else None,
                    }
                    trusts.append(trust)
            return trusts
        except:
            return []
    
    def _get_domain_functional_level(self, domain_dn: str) -> Optional[str]:
        """Get the functional level of a domain."""
        try:
            success = self._conn.search(
                search_base=domain_dn,
                search_filter="(objectClass=domain)",
                search_scope='BASE',
                attributes=['msDS-Behavior-Version']
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'msDS-Behavior-Version') and entry.__dict__.get('msDS-Behavior-Version'):
                    level = str(entry.__dict__['msDS-Behavior-Version'].value)
                    # Map functional levels to readable names
                    level_map = {
                        "0": "2000",
                        "1": "2003 Interim",
                        "2": "2003",
                        "3": "2008",
                        "4": "2008 R2",
                        "5": "2012",
                        "6": "2012 R2",
                        "7": "2016",
                        "10": "2019",
                        "11": "2022"
                    }
                    return level_map.get(level, f"Unknown ({level})")
            return None
        except:
            return None
    
    def _get_forest_name(self) -> Optional[str]:
        """Get the forest DNS name."""
        try:
            config_context = self._conn.server.info.other.get('configurationNamingContext', [''])[0]
            search_base = f"CN=Partitions,{config_context}"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter="(&(objectClass=crossRef)(systemFlags:1.2.840.113556.1.4.803:=2)(nETBIOSName=*))",
                search_scope=SUBTREE,
                attributes=['dnsRoot']
            )
            
            if success and self._conn.entries:
                # The first domain is typically the forest root
                entry = self._conn.entries[0]
                if hasattr(entry, 'dnsRoot') and entry.dnsRoot:
                    return str(entry.dnsRoot.value)
            return None
        except:
            return None
    
    def _strip_guid_parents(self, guid_value: str) -> str:
        """Remove curly braces from GUID if present."""
        if isinstance(guid_value, str):
            return guid_value.strip('{}')
        return str(guid_value).strip('{}')
