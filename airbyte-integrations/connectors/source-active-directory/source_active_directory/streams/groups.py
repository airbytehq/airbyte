from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class Groups(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "groups"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Group's unique objectGUID identifier"},
                "name": {"type": ["string", "null"], "description": "Group's display name"},
                "sam_account_name": {"type": ["string", "null"], "description": "sAMAccountName"},
                "description": {"type": ["string", "null"], "description": "Group description"},
                "group_type": {"type": ["string", "null"], "description": "Group type (Security/Distribution)"},
                "group_scope": {"type": ["string", "null"], "description": "Group scope (Domain Local/Global/Universal)"},
                "created_at": {"type": ["string", "null"], "description": "Group creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Last modification time"},
                "members": {"type": ["array"], "items": {"type": "string"}, "description": "Member object IDs"},
                "member_of": {"type": ["array"], "items": {"type": "string"}, "description": "Parent group object IDs"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read groups from Active Directory using LDAP search."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to get group objects
            search_filter = "(objectClass=group)"
            
            # Attributes to retrieve for each group
            attributes = [
                'objectGUID',           # Unique identifier
                'sAMAccountName',       # Group name
                'displayName',          # Display name
                'cn',                   # Common name
                'description',          # Description
                'groupType',            # Group type flags
                'whenCreated',          # Creation time
                'whenChanged',          # Last modified time
                'member',               # Group members
                'memberOf'              # Groups this group belongs to
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
            
            # Process each group entry
            for entry in self._conn.entries:
                # Extract objectGUID as the primary ID
                object_guid = entry.objectGUID
                if not object_guid:
                    raise ValueError(f"Group entry missing objectGUID: {entry.entry_dn}")
                
                # Get member object IDs from member DNs
                member_object_ids = []
                if hasattr(entry, 'member') and entry.member:
                    for member_dn in entry.member:
                        try:
                            # Query each member to get its objectGUID
                            member_search_success = self._conn.search(
                                search_base=str(member_dn),
                                search_filter="(objectClass=*)",
                                search_scope='BASE',
                                attributes=['objectGUID']
                            )
                            
                            if member_search_success and self._conn.entries:
                                member_entry = self._conn.entries[0]
                                if hasattr(member_entry, 'objectGUID') and member_entry.objectGUID:
                                    member_object_ids.append(self._strip_guid_parents(str(member_entry.objectGUID)))
                        except Exception as e:
                            self.logger.warning(f"Failed to get objectGUID for member {member_dn}: {str(e)}")
                            continue
                
                # Get parent group object IDs from memberOf DNs
                parent_group_object_ids = []
                if hasattr(entry, 'memberOf') and entry.memberOf:
                    for group_dn in entry.memberOf:
                        try:
                            # Query each parent group to get its objectGUID
                            group_search_success = self._conn.search(
                                search_base=str(group_dn),
                                search_filter="(objectClass=group)",
                                search_scope='BASE',
                                attributes=['objectGUID']
                            )
                            
                            if group_search_success and self._conn.entries:
                                group_entry = self._conn.entries[0]
                                if hasattr(group_entry, 'objectGUID') and group_entry.objectGUID:
                                    parent_group_object_ids.append(self._strip_guid_parents(str(group_entry.objectGUID)))
                        except Exception as e:
                            self.logger.warning(f"Failed to get objectGUID for parent group {group_dn}: {str(e)}")
                            continue
                
                # Parse group type from groupType attribute
                group_type_info = self._parse_group_type(entry.groupType.value if entry.groupType else None)
                
                # Build the group record
                group_record = {
                    "id": self._strip_guid_parents(str(object_guid)),
                    "name": str(entry.displayName) if entry.displayName else str(entry.cn) if entry.cn else None,
                    "sam_account_name": str(entry.sAMAccountName) if entry.sAMAccountName else None,
                    "description": str(entry.description) if entry.description else None,
                    "group_type": group_type_info["type"],
                    "group_scope": group_type_info["scope"],
                    "created_at": str(entry.whenCreated) if entry.whenCreated else None,
                    "modified_at": str(entry.whenChanged) if entry.whenChanged else None,
                    "members": member_object_ids,
                    "member_of": parent_group_object_ids
                }
                
                yield group_record
                    
        except Exception as e:
            self.logger.error(f"Error during LDAP search: {str(e)}")
            raise
    
    def _parse_group_type(self, group_type_value: Optional[int]) -> dict:
        """Parse Active Directory groupType attribute into readable format."""
        if group_type_value is None:
            return {"type": None, "scope": None}
        
        # Group type flags according to Microsoft documentation
        # https://docs.microsoft.com/en-us/windows/win32/adschema/a-grouptype
        
        # Security vs Distribution
        if group_type_value & 0x80000000:  # -2147483648 (security group)
            group_type = "Security"
        else:
            group_type = "Distribution"
        
        # Group scope
        if group_type_value & 0x00000004:  # Domain Local
            scope = "Domain Local"
        elif group_type_value & 0x00000002:  # Global
            scope = "Global"
        elif group_type_value & 0x00000008:  # Universal
            scope = "Universal"
        else:
            scope = "Unknown"
        
        return {"type": group_type, "scope": scope}
