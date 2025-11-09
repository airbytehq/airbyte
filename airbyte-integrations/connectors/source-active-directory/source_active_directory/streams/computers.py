from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Computers(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "computers"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Computer's unique objectGUID identifier"},
                "name": {"type": ["string", "null"], "description": "Computer's display name"},
                "computer_name": {"type": ["string"], "description": "sAMAccountName"},
                "dns_hostname": {"type": ["string", "null"], "description": "DNS hostname of the computer"},
                "operating_system": {"type": ["string", "null"], "description": "Operating system name"},
                "operating_system_version": {"type": ["string", "null"], "description": "Operating system version"},
                "operating_system_service_pack": {"type": ["string", "null"], "description": "Operating system service pack"},
                "distinguished_name": {"type": ["string", "null"], "description": "Distinguished name of the computer"},
                "description": {"type": ["string", "null"], "description": "Computer description"},
                "created_at": {"type": ["string"], "description": "Computer account creation time"},
                "modified_at": {"type": ["string"], "description": "Last modification time"},
                "last_logon": {"type": ["string", "null"], "description": "Last logon timestamp"},
                "password_last_set": {"type": ["string", "null"], "description": "Password last set timestamp"},
                "enabled": {"type": ["boolean"], "description": "Computer account enabled status"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read computers from Active Directory using LDAP search."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to get computer objects
            search_filter = "(&(objectClass=computer)(objectCategory=computer))"
            
            # Attributes to retrieve for each computer
            attributes = [
                'objectGUID',                    # Unique identifier
                'sAMAccountName',                # Computer name
                'cn',                            # Common name
                'dNSHostName',                   # DNS hostname
                'distinguishedName',             # Distinguished name
                'displayName',                   # Display name
                'description',                   # Description
                'operatingSystem',               # Operating system
                'operatingSystemVersion',        # OS version
                'operatingSystemServicePack',    # OS service pack
                'whenCreated',                   # Creation time
                'whenChanged',                   # Last modified time
                'lastLogon',                     # Last logon time
                'lastLogonTimestamp',            # Last logon timestamp
                'pwdLastSet',                    # Password last set
                'userAccountControl',            # Account control flags
            ]
            
            # Perform the LDAP search
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            if not success:
                self.logger.error(f"LDAP search failed: {self._conn.result}")
                return
            
            # Process each computer entry
            for entry in self._conn.entries:
                # Extract objectGUID as the primary ID
                object_guid = entry.objectGUID
                if not object_guid:
                    raise ValueError(f"Computer entry missing objectGUID: {entry.entry_dn}")
                
                # Convert lastLogon and pwdLastSet from Windows timestamp to readable format
                last_logon = None
                if hasattr(entry, 'lastLogon') and entry.lastLogon.value:
                    last_logon = entry.lastLogon.value
                elif hasattr(entry, 'lastLogonTimestamp') and entry.lastLogonTimestamp.value:
                    last_logon = entry.lastLogonTimestamp.value
                
                password_last_set = None
                if hasattr(entry, 'pwdLastSet') and entry.pwdLastSet.value:
                    password_last_set = entry.pwdLastSet.value
                
                # Build the computer record
                computer_record = {
                    "id": self._strip_guid_parents(object_guid.value),
                    "name": entry.displayName.value if hasattr(entry, 'displayName') else entry.cn.value,
                    "computer_name": entry.sAMAccountName.value,
                    "dns_hostname": entry.dNSHostName.value if hasattr(entry, 'dNSHostName') else None,
                    "operating_system": entry.operatingSystem.value if hasattr(entry, 'operatingSystem') else None,
                    "operating_system_version": entry.operatingSystemVersion.value if hasattr(entry, 'operatingSystemVersion') else None,
                    "operating_system_service_pack": entry.operatingSystemServicePack.value if hasattr(entry, 'operatingSystemServicePack') else None,
                    "distinguished_name": entry.distinguishedName.value,
                    "description": entry.description.value if hasattr(entry, 'description') else None,
                    "created_at": entry.whenCreated.value,
                    "modified_at": entry.whenChanged.value,
                    "last_logon": last_logon,
                    "password_last_set": password_last_set,
                    "enabled": bool(int(entry.userAccountControl.value)) & 2 == 0 if hasattr(entry, 'userAccountControl') else True,
                }
                
                yield computer_record
                    
                    
        except Exception as e:
            self.logger.error(f"Error during LDAP search: {str(e)}")
            raise