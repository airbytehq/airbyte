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
                "user_id": {"type": ["string"], "description": "User's objectGUID identifier"},
                "group_id": {"type": ["string"], "description": "Group's objectGUID identifier"},
                "user_name": {"type": ["string", "null"], "description": "User's display name"},
                "user_username": {"type": ["string", "null"], "description": "User's sAMAccountName"},
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
        """Read group memberships from Active Directory using LDAP search."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
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
                
                user_id = self._strip_guid_parents(user_object_guid.value)
                user_name = user_entry.displayName.value if hasattr(user_entry, 'displayName') else None
                user_username = user_entry.sAMAccountName.value if hasattr(user_entry, 'sAMAccountName') else None
                
                # Process memberOf groups
                if hasattr(user_entry, 'memberOf') and user_entry.memberOf:
                    for group_dn in user_entry.memberOf:
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
                                    membership_id = f"{user_id}_{group_id}"
                                    
                                    membership_record = {
                                        "id": membership_id,
                                        "user_id": user_id,
                                        "group_id": group_id,
                                        "user_name": user_name,
                                        "user_username": user_username,
                                        "group_name": group_entry.displayName.value if hasattr(group_entry, 'displayName') else None,
                                        "group_description": group_entry.description.value if hasattr(group_entry, 'description') else None,
                                        "group_type": group_type,
                                        "group_scope": group_scope,
                                        "membership_added_at": group_entry.whenCreated.value if hasattr(group_entry, 'whenCreated') else None,
                                        "is_primary_group": False  # memberOf groups are not primary
                                    }
                                    
                                    yield membership_record
                                    
                        except Exception as e:
                            self.logger.warning(f"Failed to get details for group {group_dn}: {str(e)}")
                            continue
                
                # Process primary group
                if hasattr(user_entry, 'primaryGroupID') and user_entry.primaryGroupID:
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
                                        membership_id = f"{user_id}_{primary_group_id}_primary"
                                        
                                        primary_membership_record = {
                                            "id": membership_id,
                                            "user_id": user_id,
                                            "group_id": primary_group_id,
                                            "user_name": user_name,
                                            "user_username": user_username,
                                            "group_name": primary_group_entry.displayName.value if hasattr(primary_group_entry, 'displayName') else None,
                                            "group_description": primary_group_entry.description.value if hasattr(primary_group_entry, 'description') else None,
                                            "group_type": group_type,
                                            "group_scope": group_scope,
                                            "membership_added_at": primary_group_entry.whenCreated.value if hasattr(primary_group_entry, 'whenCreated') else None,
                                            "is_primary_group": True
                                        }
                                        
                                        yield primary_membership_record
                                        
                    except Exception as e:
                        self.logger.warning(f"Failed to process primary group for user {user_id}: {str(e)}")
                        continue
                    
        except Exception as e:
            self.logger.error(f"Error during group membership LDAP search: {str(e)}")
            raise

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
