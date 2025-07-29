from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class GroupMemberships(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "group_memberships"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Unique identifier for this membership relationship"},
                "principal_id": {"type": ["string"], "description": "Principal's objectGUID identifier (user or group)"},
                "principal_name": {"type": ["string", "null"], "description": "Principal's display name"},
                "principal_type": {"type": ["string"], "description": "Principal type (user/group)"},
                "principal_username": {"type": ["string", "null"], "description": "Principal's sAMAccountName (for users)"},
                "group_id": {"type": ["string"], "description": "Group's objectGUID identifier"},
                "group_name": {"type": ["string", "null"], "description": "Group's display name"},
                "group_description": {"type": ["string", "null"], "description": "Group's description"},
                "group_type": {"type": ["string", "null"], "description": "Group type (security/distribution)"},
                "group_scope": {"type": ["string", "null"], "description": "Group scope (global/domain local/universal)"},
                "membership_added_at": {"type": ["string", "null"], "description": "When the membership was added"},
                "is_primary_group": {"type": ["boolean"], "description": "Whether this is the user's primary group"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read group memberships from Active Directory using LDAP search for both users and groups."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # Process users as principals
            yield from self._process_user_principals(search_base)
            
            # Process groups as principals
            yield from self._process_group_principals(search_base)
                    
        except Exception as e:
            self.logger.error(f"Error during group membership LDAP search: {str(e)}")
            raise

    def _process_user_principals(self, search_base: str) -> Iterable[Mapping[str, Any]]:
        """Process users as principals in group memberships."""
        
        # LDAP filter to get user objects
        # This filter looks for person objects that are users but excludes computer accounts
        search_filter = "(&(objectClass=user)(objectCategory=person)(!(objectClass=computer)))"
        
        # Attributes to retrieve for each user
        user_attributes = [
            'objectGUID',           # Unique identifier
            'sAMAccountName',       # Username
            'displayName',          # Display name
            'memberOf',             # Group memberships
            'primaryGroupID'        # Primary group ID
        ]
        
        # Perform the LDAP search for users
        success = self._conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=user_attributes
        )
        
        if not success:
            self.logger.error(f"LDAP search for users failed: {self._conn.result}")
            return
        
        # Process each user entry
        for user_entry in self._conn.entries:
            # Extract user objectGUID as the primary ID
            user_object_guid = user_entry.objectGUID
            if not user_object_guid:
                self.logger.warning(f"User entry missing objectGUID: {user_entry.entry_dn}")
                continue
            
            principal_id = self._strip_guid_parents(user_object_guid.value)
            principal_name = user_entry.displayName.value if hasattr(user_entry, 'displayName') else None
            principal_username = user_entry.sAMAccountName.value if hasattr(user_entry, 'sAMAccountName') else None
            
            # Process memberOf groups
            if hasattr(user_entry, 'memberOf') and user_entry.memberOf:
                for group_dn in user_entry.memberOf:
                    membership_record = self._create_membership_record_from_group_dn(
                        group_dn, principal_id, principal_name, "user", principal_username, False
                    )
                    if membership_record:
                        yield membership_record
            
            # Process primary group
            if hasattr(user_entry, 'primaryGroupID') and user_entry.primaryGroupID:
                primary_membership_record = self._process_primary_group(
                    user_entry, search_base, principal_id, principal_name, "user", principal_username
                )
                if primary_membership_record:
                    yield primary_membership_record

    def _process_group_principals(self, search_base: str) -> Iterable[Mapping[str, Any]]:
        """Process groups as principals in group memberships."""
        
        # LDAP filter to get group objects
        search_filter = "(objectClass=group)"
        
        # Attributes to retrieve for each group
        group_attributes = [
            'objectGUID',           # Unique identifier
            'sAMAccountName',       # Group name
            'displayName',          # Display name
            'memberOf'              # Group memberships
        ]
        
        # Perform the LDAP search for groups
        success = self._conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=group_attributes
        )
        
        if not success:
            self.logger.error(f"LDAP search for groups failed: {self._conn.result}")
            return
        
        # Process each group entry
        for group_entry in self._conn.entries:
            # Extract group objectGUID as the primary ID
            group_object_guid = group_entry.objectGUID
            if not group_object_guid:
                self.logger.warning(f"Group entry missing objectGUID: {group_entry.entry_dn}")
                continue
            
            principal_id = self._strip_guid_parents(group_object_guid.value)
            principal_name = group_entry.displayName.value if hasattr(group_entry, 'displayName') else None
            principal_username = group_entry.sAMAccountName.value if hasattr(group_entry, 'sAMAccountName') else None
            
            # Process memberOf groups (groups that this group is a member of)
            if hasattr(group_entry, 'memberOf') and group_entry.memberOf:
                for parent_group_dn in group_entry.memberOf:
                    membership_record = self._create_membership_record_from_group_dn(
                        parent_group_dn, principal_id, principal_name, "group", principal_username, False
                    )
                    if membership_record:
                        yield membership_record

    def _create_membership_record_from_group_dn(
        self, 
        group_dn: str, 
        principal_id: str, 
        principal_name: str, 
        principal_type: str,
        principal_username: str,
        is_primary_group: bool
    ) -> Optional[Mapping[str, Any]]:
        """Create a membership record from a group DN."""
        try:
            # Query each group to get detailed information
            group_search_success = self._conn.search(
                search_base=str(group_dn),
                search_filter="(objectClass=group)",
                search_scope='BASE',
                attributes=[
                    'objectGUID',
                    'displayName',
                    'description',
                    'groupType',
                    'whenCreated'
                ]
            )
            
            if group_search_success and self._conn.entries:
                group_entry = self._conn.entries[0]
                if hasattr(group_entry, 'objectGUID') and group_entry.objectGUID:
                    group_id = self._strip_guid_parents(group_entry.objectGUID.value)
                    
                    # Determine group type and scope from groupType attribute
                    group_type_value = getattr(group_entry, 'groupType', None)
                    group_type, group_scope = self._parse_group_type(group_type_value.value if group_type_value else None)
                    
                    # Create unique ID for this membership relationship
                    membership_id = f"{principal_id}_{group_id}"
                    if is_primary_group:
                        membership_id += "_primary"
                    
                    membership_record = {
                        "id": membership_id,
                        "principal_id": principal_id,
                        "principal_name": principal_name,
                        "principal_type": principal_type,
                        "principal_username": principal_username,
                        "group_id": group_id,
                        "group_name": group_entry.displayName.value if hasattr(group_entry, 'displayName') else None,
                        "group_description": group_entry.description.value if hasattr(group_entry, 'description') else None,
                        "group_type": group_type,
                        "group_scope": group_scope,
                        "membership_added_at": group_entry.whenCreated.value if hasattr(group_entry, 'whenCreated') else None,
                        "is_primary_group": is_primary_group,
                    }
                    
                    return membership_record
                    
        except Exception as e:
            self.logger.warning(f"Failed to get details for group {group_dn}: {str(e)}")
            
        return None

    def _process_primary_group(
        self, 
        user_entry, 
        search_base: str, 
        principal_id: str, 
        principal_name: str, 
        principal_type: str,
        principal_username: str
    ) -> Optional[Mapping[str, Any]]:
        """Process primary group membership for a user."""
        try:
            # Get domain SID to construct primary group SID
            domain_info = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # Search for the domain object to get domain SID
            domain_search_success = self._conn.search(
                search_base=domain_info,
                search_filter="(objectClass=domain)",
                search_scope='BASE',
                attributes=['objectSid']
            )
            
            if domain_search_success and self._conn.entries:
                domain_entry = self._conn.entries[0]
                if hasattr(domain_entry, 'objectSid'):
                    # Construct primary group SID
                    domain_sid = str(domain_entry.objectSid.value)
                    primary_group_rid = str(user_entry.primaryGroupID.value)
                    primary_group_sid = f"{domain_sid}-{primary_group_rid}"
                    
                    # Search for the primary group by SID
                    primary_group_search = self._conn.search(
                        search_base=search_base,
                        search_filter=f"(&(objectClass=group)(objectSid={primary_group_sid}))",
                        search_scope=SUBTREE,
                        attributes=[
                            'objectGUID',
                            'displayName',
                            'description',
                            'groupType',
                            'whenCreated'
                        ]
                    )
                    
                    if primary_group_search and self._conn.entries:
                        primary_group_entry = self._conn.entries[0]
                        if hasattr(primary_group_entry, 'objectGUID'):
                            primary_group_id = self._strip_guid_parents(primary_group_entry.objectGUID.value)
                            
                            # Determine group type and scope
                            group_type_value = getattr(primary_group_entry, 'groupType', None)
                            group_type, group_scope = self._parse_group_type(group_type_value.value if group_type_value else None)
                            
                            # Create unique ID for primary group membership
                            membership_id = f"{principal_id}_{primary_group_id}_primary"
                            
                            primary_membership_record = {
                                "id": membership_id,
                                "principal_id": principal_id,
                                "principal_name": principal_name,
                                "principal_type": principal_type,
                                "principal_username": principal_username,
                                "group_id": primary_group_id,
                                "group_name": primary_group_entry.displayName.value if hasattr(primary_group_entry, 'displayName') else None,
                                "group_description": primary_group_entry.description.value if hasattr(primary_group_entry, 'description') else None,
                                "group_type": group_type,
                                "group_scope": group_scope,
                                "membership_added_at": primary_group_entry.whenCreated.value if hasattr(primary_group_entry, 'whenCreated') else None,
                                "is_primary_group": True
                            }
                            
                            return primary_membership_record
                            
        except Exception as e:
            self.logger.warning(f"Failed to process primary group for principal {principal_id}: {str(e)}")
            
        return None

    def _parse_group_type(self, group_type_value: int) -> tuple[str, str]:
        """
        Parse the groupType attribute to determine group type and scope.
        
        :param group_type_value: The groupType attribute value from AD
        :return: Tuple of (group_type, group_scope)
        """
        if group_type_value is None:
            return "unknown", "unknown"
            
        # Group type flags
        SECURITY_ENABLED = 0x80000000
        
        # Group scope flags
        GLOBAL_GROUP = 0x00000002
        DOMAIN_LOCAL_GROUP = 0x00000004
        UNIVERSAL_GROUP = 0x00000008
        
        # Determine if it's a security or distribution group
        group_type = "security" if (group_type_value & SECURITY_ENABLED) else "distribution"
        
        # Determine group scope
        if group_type_value & GLOBAL_GROUP:
            group_scope = "global"
        elif group_type_value & DOMAIN_LOCAL_GROUP:
            group_scope = "domain_local"
        elif group_type_value & UNIVERSAL_GROUP:
            group_scope = "universal"
        else:
            group_scope = "unknown"
            
        return group_type, group_scope
