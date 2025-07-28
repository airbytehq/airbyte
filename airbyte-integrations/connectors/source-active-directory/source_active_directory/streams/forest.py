from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Forest(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "forest"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Forest's unique identifier"},
                "name": {"type": ["string"], "description": "Forest DNS name"},
                "forest_mode": {"type": ["string", "null"], "description": "Forest functional level"},
                "schema_version": {"type": ["string", "null"], "description": "Schema version"},
                "root_domain": {"type": ["string", "null"], "description": "Forest root domain"},
                "domains": {"type": ["array"], "items": {"type": "string"}, "description": "List of domain names in forest"},
                "global_catalogs": {"type": ["array"], "items": {"type": "string"}, "description": "Global catalog servers"},
                "sites": {"type": ["array"], "items": {"type": "string"}, "description": "AD sites in forest"},
                "created_at": {"type": ["string", "null"], "description": "Forest creation time"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read forest information from Active Directory."""
        
        try:
            # Get configuration and root domain naming contexts
            config_context = self._conn.server.info.other.get('configurationNamingContext', [''])[0]
            root_domain_context = self._conn.server.info.other.get('rootDomainNamingContext', [''])[0]
            
            # Get forest information from the root domain
            forest_info = self._get_forest_info(config_context, root_domain_context)
            
            if forest_info:
                yield forest_info
                    
        except Exception as e:
            self.logger.error(f"Error during forest search: {str(e)}")
            raise
    
    def _get_forest_info(self, config_context: str, root_domain_context: str) -> dict:
        """Get comprehensive forest information."""
        try:
            # Get forest root domain name
            forest_name = self._get_forest_name(config_context)
            
            # Get forest functional level
            forest_mode = self._get_forest_functional_level(config_context)
            
            # Get schema version
            schema_version = self._get_schema_version(config_context)
            
            # Get all domains in forest
            domains = self._get_forest_domains(config_context)
            
            # Get global catalog servers
            global_catalogs = self._get_global_catalogs(config_context)
            
            # Get AD sites
            sites = self._get_ad_sites(config_context)
            
            # Get forest creation time (approximate from root domain)
            creation_time = self._get_forest_creation_time(root_domain_context)
            
            forest_record = {
                "id": f"forest-{forest_name}" if forest_name else "forest-unknown",
                "name": forest_name,
                "forest_mode": forest_mode,
                "schema_version": schema_version,
                "root_domain": forest_name,  # Root domain is the same as forest name
                "domains": domains,
                "global_catalogs": global_catalogs,
                "sites": sites,
                "created_at": creation_time,
            }
            
            return forest_record
            
        except Exception as e:
            self.logger.error(f"Error getting forest info: {str(e)}")
            return None
    
    def _get_forest_name(self, config_context: str) -> Optional[str]:
        """Get the forest DNS name."""
        try:
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
    
    def _get_forest_functional_level(self, config_context: str) -> Optional[str]:
        """Get forest functional level."""
        try:
            search_base = f"CN=Partitions,{config_context}"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter="(objectClass=crossRefContainer)",
                search_scope='BASE',
                attributes=['msDS-Behavior-Version']
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'msDS-Behavior-Version') and entry.__dict__.get('msDS-Behavior-Version'):
                    level = str(entry.__dict__['msDS-Behavior-Version'].value)
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
    
    def _get_schema_version(self, config_context: str) -> Optional[str]:
        """Get Active Directory schema version."""
        try:
            search_base = f"CN=Schema,{config_context}"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter="(objectClass=dMD)",
                search_scope='BASE',
                attributes=['objectVersion']
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'objectVersion') and entry.objectVersion:
                    version = str(entry.objectVersion.value)
                    # Map common schema versions
                    version_map = {
                        "13": "Windows 2000",
                        "30": "Windows 2003",
                        "31": "Windows 2003 R2",
                        "44": "Windows 2008",
                        "47": "Windows 2008 R2",
                        "56": "Windows 2012",
                        "69": "Windows 2012 R2",
                        "87": "Windows 2016",
                        "88": "Windows 2019",
                        "89": "Windows 2022"
                    }
                    return version_map.get(version, f"Version {version}")
            return None
        except:
            return None
    
    def _get_forest_domains(self, config_context: str) -> list:
        """Get all domains in the forest."""
        try:
            search_base = f"CN=Partitions,{config_context}"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter="(&(objectClass=crossRef)(systemFlags:1.2.840.113556.1.4.803:=2))",
                search_scope=SUBTREE,
                attributes=['dnsRoot']
            )
            
            domains = []
            if success:
                for entry in self._conn.entries:
                    if hasattr(entry, 'dnsRoot') and entry.dnsRoot:
                        domains.append(str(entry.dnsRoot.value))
            return domains
        except:
            return []
    
    def _get_global_catalogs(self, config_context: str) -> list:
        """Get global catalog servers."""
        try:
            search_base = f"CN=Sites,{config_context}"
            search_filter = "(&(objectClass=nTDSDSA)(options:1.2.840.113556.1.4.803:=1))"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            gc_servers = []
            if success:
                for entry in self._conn.entries:
                    # Get the server name from the parent container
                    server_dn = entry.entry_dn
                    server_name = server_dn.split(',')[1].replace('CN=', '') if ',' in server_dn else None
                    if server_name:
                        gc_servers.append(server_name)
            return gc_servers
        except:
            return []
    
    def _get_ad_sites(self, config_context: str) -> list:
        """Get Active Directory sites."""
        try:
            search_base = f"CN=Sites,{config_context}"
            search_filter = "(objectClass=site)"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            sites = []
            if success:
                for entry in self._conn.entries:
                    if hasattr(entry, 'cn') and entry.cn:
                        sites.append(str(entry.cn.value))
            return sites
        except:
            return []
    
    def _get_forest_creation_time(self, root_domain_context: str) -> Optional[str]:
        """Get approximate forest creation time from root domain."""
        try:
            success = self._conn.search(
                search_base=root_domain_context,
                search_filter="(objectClass=domain)",
                search_scope='BASE',
                attributes=['whenCreated']
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'whenCreated') and entry.whenCreated:
                    return str(entry.whenCreated.value)
            return None
        except:
            return None
