from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Sites(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "sites"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Site's unique objectGUID identifier"},
                "name": {"type": ["string"], "description": "Site name"},
                "description": {"type": ["string", "null"], "description": "Site description"},
                "location": {"type": ["string", "null"], "description": "Site location"},
                "subnets": {"type": ["array"], "items": {"type": "string"}, "description": "IP subnets in this site"},
                "domain_controllers": {"type": ["array"], "items": {"type": "string"}, "description": "Domain controllers in this site"},
                "site_links": {"type": ["array"], "items": {"type": "string"}, "description": "Site links connected to this site"},
                "created_at": {"type": ["string", "null"], "description": "Site creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Last modification time"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read Active Directory sites information."""
        
        try:
            # Get configuration naming context
            config_context = self._conn.server.info.other.get('configurationNamingContext', [''])[0]
            search_base = f"CN=Sites,{config_context}"
            
            # Search for site objects
            search_filter = "(objectClass=site)"
            
            attributes = [
                'objectGUID',
                'cn',
                'description',
                'location',
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
                self.logger.error(f"Failed to search for sites: {self._conn.result}")
                return
            
            for entry in self._conn.entries:
                try:
                    object_guid = entry.objectGUID
                    if not object_guid:
                        continue
                    
                    site_name = str(entry.cn.value) if hasattr(entry, 'cn') and entry.cn else None
                    
                    # Get subnets for this site
                    subnets = self._get_site_subnets(config_context, site_name) if site_name else []
                    
                    # Get domain controllers in this site
                    domain_controllers = self._get_site_domain_controllers(config_context, site_name) if site_name else []
                    
                    # Get site links for this site
                    site_links = self._get_site_links(config_context, site_name) if site_name else []
                    
                    site_record = {
                        "id": self._strip_guid_parents(object_guid.value),
                        "name": site_name,
                        "description": str(entry.description.value) if hasattr(entry, 'description') and entry.description else None,
                        "location": str(entry.location.value) if hasattr(entry, 'location') and entry.location else None,
                        "subnets": subnets,
                        "domain_controllers": domain_controllers,
                        "site_links": site_links,
                        "created_at": str(entry.whenCreated.value) if hasattr(entry, 'whenCreated') and entry.whenCreated else None,
                        "modified_at": str(entry.whenChanged.value) if hasattr(entry, 'whenChanged') and entry.whenChanged else None,
                    }
                    
                    yield site_record
                    
                except Exception as e:
                    self.logger.warning(f"Error processing site entry {entry.entry_dn}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during sites search: {str(e)}")
            raise
    
    def _get_site_subnets(self, config_context: str, site_name: str) -> list:
        """Get IP subnets associated with a site."""
        try:
            search_base = f"CN=Subnets,CN=Sites,{config_context}"
            search_filter = f"(&(objectClass=subnet)(siteObject=CN={site_name},CN=Sites,{config_context}))"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            subnets = []
            if success:
                for entry in self._conn.entries:
                    if hasattr(entry, 'cn') and entry.cn:
                        subnets.append(str(entry.cn.value))
            return subnets
        except:
            return []
    
    def _get_site_domain_controllers(self, config_context: str, site_name: str) -> list:
        """Get domain controllers in a specific site."""
        try:
            search_base = f"CN={site_name},CN=Sites,{config_context}"
            search_filter = "(objectClass=server)"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            domain_controllers = []
            if success:
                for entry in self._conn.entries:
                    if hasattr(entry, 'cn') and entry.cn:
                        domain_controllers.append(str(entry.cn.value))
            return domain_controllers
        except:
            return []
    
    def _get_site_links(self, config_context: str, site_name: str) -> list:
        """Get site links that connect to this site."""
        try:
            search_base = f"CN=Inter-Site Transports,CN=Sites,{config_context}"
            search_filter = f"(&(objectClass=siteLink)(siteList=CN={site_name},CN=Sites,{config_context}))"
            
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn']
            )
            
            site_links = []
            if success:
                for entry in self._conn.entries:
                    if hasattr(entry, 'cn') and entry.cn:
                        site_links.append(str(entry.cn.value))
            return site_links
        except:
            return []
    
    def _strip_guid_parents(self, guid_value: str) -> str:
        """Remove curly braces from GUID if present."""
        if isinstance(guid_value, str):
            return guid_value.strip('{}')
        return str(guid_value).strip('{}')
