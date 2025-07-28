from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Users(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "users"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "User's unique objectGUID identifier"},
                "name": {"type": ["string", "null"], "description": "User's display name"},
                "username": {"type": ["string"], "description": "sAMAccountName"},
                "email": {"type": ["string", "null"], "description": "User's email address"},
                "first_name": {"type": ["string", "null"], "description": "Given name"},
                "last_name": {"type": ["string", "null"], "description": "Surname"},
                "user_principal_name": {"type": ["string", "null"], "description": "UPN"},
                "created_at": {"type": ["string"], "description": "Account creation time"},
                "modified_at": {"type": ["string"], "description": "Last modification time"},
                "enabled": {"type": ["boolean"], "description": "Account enabled status"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read users from Active Directory using LDAP search."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to get user objects
            # This filter looks for person objects that are users but excludes computer accounts
            search_filter = "(&(objectClass=user)(objectCategory=person)(!(objectClass=computer)))"
            
            # Attributes to retrieve for each user
            attributes = [
                'objectGUID',           # Unique identifier
                'sAMAccountName',       # Username
                'userPrincipalName',    # User principal name
                'displayName',          # Display name
                'cn',                   # Common name
                'givenName',            # First name
                'sn',                   # Last name
                'mail',                 # Email address
                'description',          # Description
                'whenCreated',          # Creation time
                'whenChanged',          # Last modified time
                'accountExpires',       # Account expiration
                'userAccountControl',   # Account control flags
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
            
            # Process each user entry
            for entry in self._conn.entries:
                # Extract objectGUID as the primary ID
                object_guid = entry.objectGUID
                if not object_guid:
                    raise ValueError(f"User entry missing objectGUID: {entry.entry_dn}")
                
                # Build the user record
                user_record = {
                    "id": self._strip_guid_parents(object_guid.value),
                    "name": entry.displayName.value,
                    "username": entry.sAMAccountName.value,
                    "email": entry.mail.value,
                    "first_name": entry.givenName.value,
                    "last_name": entry.sn.value,
                    "user_principal_name": entry.userPrincipalName.value,
                    "created_at": entry.whenCreated.value,
                    "modified_at": entry.whenChanged.value,
                    "enabled": bool(int(entry.userAccountControl.value)) & 2 == 0,
                }
                
                yield user_record
                    
                    
        except Exception as e:
            self.logger.error(f"Error during LDAP search: {str(e)}")
            raise