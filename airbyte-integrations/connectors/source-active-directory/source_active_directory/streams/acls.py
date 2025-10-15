import struct

from typing import Any, Iterable, Mapping, Optional, List, Dict

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class ACLs(ActiveDirectoryStream):
    """Stream for extracting Access Control Lists (ACLs) from Active Directory objects."""
    
    @property
    def name(self) -> str:
        return "acls"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Unique identifier for this ACL entry"},
                "resource_id": {"type": ["string"], "description": "ObjectGUID of the resource object"},
                "resource_dn": {"type": ["string"], "description": "Distinguished name of the resource"},
                "resource_type": {"type": ["string"], "description": "Object class of the resource"},
                "principal_sid": {"type": ["string"], "description": "SID of the principal (user/group/computer)"},
                "principal_id": {"type": ["string", "null"], "description": "ObjectGUID of the principal object"},
                "principal_type": {"type": ["string"], "description": "Type of principal (User, Group, Computer, etc.)"},
                "ace_type": {"type": ["string"], "description": "Access Control Entry type (Allow, Deny, etc.)"},
                "permissions": {"type": ["array"], "items": {"type": "string"}, "description": "List of permissions granted"},
                "access_mask": {"type": ["integer"], "description": "Raw access mask value"},
                "inheritance_flags": {"type": ["array"], "items": {"type": "string"}, "description": "Inheritance flags"},
                "is_inherited": {"type": ["boolean"], "description": "Whether this ACE is inherited"},
                "created_at": {"type": ["string", "null"], "description": "Resource creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Resource last modification time"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read ACLs from Active Directory security descriptors."""
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to get all objects with security descriptors
            # We'll focus on common object types that have meaningful ACLs
            search_filter = "(|(objectClass=user)(objectClass=group)(objectClass=computer)(objectClass=organizationalUnit)(objectClass=container))"
            
            # Attributes to retrieve for each object
            attributes = [
                'objectGUID',           # Unique identifier
                'distinguishedName',    # DN
                'objectClass',          # Object type
                'nTSecurityDescriptor', # Security descriptor
                'whenCreated',          # Creation time
                'whenChanged',          # Last modified time
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
            
            # Process each object entry
            for entry in self._conn.entries:
                # Extract basic object information
                object_guid = entry.objectGUID
                if not object_guid:
                    self.logger.warning(f"Object entry missing objectGUID: {entry.entry_dn}")
                    continue
                
                resource_id = self._strip_guid_parents(str(object_guid))
                resource_dn = str(entry.distinguishedName) if entry.distinguishedName else str(entry.entry_dn)
                
                # Determine primary object class
                object_classes = entry.objectClass.values if hasattr(entry, 'objectClass') and entry.objectClass else []
                resource_type = self._get_primary_object_class(object_classes)
                
                # Extract security descriptor
                if not hasattr(entry, 'nTSecurityDescriptor') or not entry.nTSecurityDescriptor:
                    self.logger.debug(f"No security descriptor found for {resource_dn}")
                    continue
                
                try:
                    # Parse the security descriptor
                    security_descriptor = entry.nTSecurityDescriptor.raw_values[0]
                    acl_entries = self._parse_security_descriptor(security_descriptor)
                    
                    # Generate ACL records for each ACE
                    for ace_info in acl_entries:
                        # Resolve principal SID to object GUID
                        principal_object_id = self._resolve_sid_to_object_id(ace_info['principal_sid'])

                        acl_record = {
                            "id": f"{resource_id}_{ace_info['ace_index']}_{ace_info['principal_sid']}",
                            "resource_id": resource_id,
                            "resource_dn": resource_dn,
                            "resource_type": resource_type,
                            "principal_sid": ace_info['principal_sid'],
                            "principal_id": principal_object_id,
                            "principal_type": ace_info['principal_type'],
                            "ace_type": ace_info['ace_type'],
                            "permissions": ace_info['permissions'],
                            "access_mask": ace_info['access_mask'],
                            "inheritance_flags": ace_info['inheritance_flags'],
                            "is_inherited": ace_info['is_inherited'],
                            "created_at": str(entry.whenCreated) if entry.whenCreated else None,
                            "modified_at": str(entry.whenChanged) if entry.whenChanged else None,
                        }
                        
                        yield acl_record
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse security descriptor for {resource_dn}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during ACL scan: {str(e)}")
            raise
    
    def _get_primary_object_class(self, object_classes: List[str]) -> str:
        """Determine the primary object class from a list of object classes."""
        # Priority order for determining primary class
        priority_classes = ['user', 'group', 'computer', 'organizationalUnit', 'container', 'domain']
        
        for priority_class in priority_classes:
            if priority_class in object_classes:
                return priority_class
        
        # Return the last (most specific) class if no priority match
        return object_classes[-1] if object_classes else 'unknown'
    
    def _parse_security_descriptor(self, security_descriptor_bytes: bytes) -> List[Dict[str, Any]]:
        """Parse a binary security descriptor to extract ACL information."""
        try:
            # Security descriptor structure according to Microsoft documentation
            # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/7d4dac05-9cef-4563-a058-f108abecce1d
            
            if len(security_descriptor_bytes) < 20:
                self.logger.warning("Security descriptor too short")
                return []
            
            # Parse security descriptor header
            revision = security_descriptor_bytes[0]
            control_flags = struct.unpack('<H', security_descriptor_bytes[2:4])[0]
            
            # Extract offsets
            owner_offset = struct.unpack('<L', security_descriptor_bytes[4:8])[0]
            group_offset = struct.unpack('<L', security_descriptor_bytes[8:12])[0]
            sacl_offset = struct.unpack('<L', security_descriptor_bytes[12:16])[0]
            dacl_offset = struct.unpack('<L', security_descriptor_bytes[16:20])[0]
            
            acl_entries = []
            
            # Parse DACL (Discretionary Access Control List) if present
            if dacl_offset > 0 and dacl_offset < len(security_descriptor_bytes):
                dacl_entries = self._parse_acl(security_descriptor_bytes, dacl_offset, "DACL")
                acl_entries.extend(dacl_entries)
            
            # Parse SACL (System Access Control List) if present
            if sacl_offset > 0 and sacl_offset < len(security_descriptor_bytes):
                sacl_entries = self._parse_acl(security_descriptor_bytes, sacl_offset, "SACL")
                acl_entries.extend(sacl_entries)
            
            return acl_entries
            
        except Exception as e:
            self.logger.warning(f"Error parsing security descriptor: {str(e)}")
            return []
    
    def _parse_acl(self, sd_bytes: bytes, acl_offset: int, acl_type: str) -> List[Dict[str, Any]]:
        """Parse an Access Control List (ACL) from the security descriptor."""
        try:
            if acl_offset + 8 > len(sd_bytes):
                return []
            
            # Parse ACL header
            acl_revision = sd_bytes[acl_offset]
            acl_size = struct.unpack('<H', sd_bytes[acl_offset + 2:acl_offset + 4])[0]
            ace_count = struct.unpack('<H', sd_bytes[acl_offset + 4:acl_offset + 6])[0]
            
            if acl_offset + acl_size > len(sd_bytes):
                return []
            
            acl_entries = []
            current_offset = acl_offset + 8  # Skip ACL header
            
            # Parse each Access Control Entry (ACE)
            for ace_index in range(ace_count):
                if current_offset + 8 > len(sd_bytes):
                    break
                
                try:
                    ace_info = self._parse_ace(sd_bytes, current_offset, ace_index, acl_type)
                    if ace_info:
                        acl_entries.append(ace_info)
                        current_offset += ace_info['ace_size']
                    else:
                        break
                except Exception as e:
                    self.logger.warning(f"Error parsing ACE {ace_index}: {str(e)}")
                    break
            
            return acl_entries
            
        except Exception as e:
            self.logger.warning(f"Error parsing ACL: {str(e)}")
            return []
    
    def _parse_ace(self, sd_bytes: bytes, ace_offset: int, ace_index: int, acl_type: str) -> Optional[Dict[str, Any]]:
        """Parse an individual Access Control Entry (ACE)."""
        try:
            if ace_offset + 8 > len(sd_bytes):
                return None
            
            # Parse ACE header
            ace_type = sd_bytes[ace_offset]
            ace_flags = sd_bytes[ace_offset + 1]
            ace_size = struct.unpack('<H', sd_bytes[ace_offset + 2:ace_offset + 4])[0]
            
            if ace_offset + ace_size > len(sd_bytes):
                return None
            
            # Parse access mask (permissions)
            access_mask = struct.unpack('<L', sd_bytes[ace_offset + 4:ace_offset + 8])[0]
            
            # Parse SID (Security Identifier)
            sid_offset = ace_offset + 8
            principal_sid = self._parse_sid(sd_bytes[sid_offset:ace_offset + ace_size])
            
            if not principal_sid:
                return None
            
            # Determine ACE type string
            ace_type_str = self._get_ace_type_string(ace_type)
            
            # Parse permissions
            permissions = self._parse_permissions(access_mask)
            
            # Parse inheritance flags
            inheritance_flags = self._parse_ace_flags(ace_flags)
            
            return {
                'ace_index': ace_index,
                'ace_size': ace_size,
                'principal_sid': principal_sid,
                'principal_type': self._determine_principal_type(principal_sid),
                'ace_type': ace_type_str,
                'permissions': permissions,
                'access_mask': access_mask,
                'inheritance_flags': inheritance_flags,
                'is_inherited': bool(ace_flags & 0x10),  # INHERITED_ACE flag
                'acl_type': acl_type
            }
            
        except Exception as e:
            self.logger.warning(f"Error parsing ACE: {str(e)}")
            return None
    
    def _parse_sid(self, sid_bytes: bytes) -> Optional[str]:
        """Parse a Security Identifier (SID) from binary format."""
        try:
            if len(sid_bytes) < 8:
                return None
            
            revision = sid_bytes[0]
            sub_authority_count = sid_bytes[1]
            
            if len(sid_bytes) < 8 + (sub_authority_count * 4):
                return None
            
            # Parse identifier authority (6 bytes, big-endian)
            identifier_authority = struct.unpack('>Q', b'\x00\x00' + sid_bytes[2:8])[0]
            
            # Parse sub-authorities (4 bytes each, little-endian)
            sub_authorities = []
            for i in range(sub_authority_count):
                offset = 8 + (i * 4)
                sub_authority = struct.unpack('<L', sid_bytes[offset:offset + 4])[0]
                sub_authorities.append(str(sub_authority))
            
            # Format as standard SID string
            sid_string = f"S-{revision}-{identifier_authority}"
            if sub_authorities:
                sid_string += "-" + "-".join(sub_authorities)
            
            return sid_string
            
        except Exception as e:
            self.logger.warning(f"Error parsing SID: {str(e)}")
            return None
    
    def _get_ace_type_string(self, ace_type: int) -> str:
        """Convert ACE type number to string."""
        ace_types = {
            0x00: "ACCESS_ALLOWED",
            0x01: "ACCESS_DENIED", 
            0x02: "SYSTEM_AUDIT",
            0x03: "SYSTEM_ALARM",
            0x04: "ACCESS_ALLOWED_COMPOUND",
            0x05: "ACCESS_ALLOWED_OBJECT",
            0x06: "ACCESS_DENIED_OBJECT",
            0x07: "SYSTEM_AUDIT_OBJECT",
            0x08: "SYSTEM_ALARM_OBJECT",
            0x09: "ACCESS_ALLOWED_CALLBACK",
            0x0A: "ACCESS_DENIED_CALLBACK",
            0x0B: "ACCESS_ALLOWED_CALLBACK_OBJECT",
            0x0C: "ACCESS_DENIED_CALLBACK_OBJECT",
            0x0D: "SYSTEM_AUDIT_CALLBACK",
            0x0E: "SYSTEM_ALARM_CALLBACK",
            0x0F: "SYSTEM_AUDIT_CALLBACK_OBJECT",
            0x10: "SYSTEM_ALARM_CALLBACK_OBJECT",
        }
        return ace_types.get(ace_type, f"UNKNOWN_{ace_type:02X}")
    
    def _parse_permissions(self, access_mask: int) -> List[str]:
        """Parse access mask into readable permission strings."""
        permissions = []
        
        # Standard rights
        if access_mask & 0x00010000:  # DELETE
            permissions.append("DELETE")
        if access_mask & 0x00020000:  # READ_CONTROL
            permissions.append("READ_CONTROL")
        if access_mask & 0x00040000:  # WRITE_DAC
            permissions.append("WRITE_DAC")
        if access_mask & 0x00080000:  # WRITE_OWNER
            permissions.append("WRITE_OWNER")
        if access_mask & 0x00100000:  # SYNCHRONIZE
            permissions.append("SYNCHRONIZE")
        
        # Generic rights
        if access_mask & 0x10000000:  # GENERIC_ALL
            permissions.append("GENERIC_ALL")
        if access_mask & 0x20000000:  # GENERIC_EXECUTE
            permissions.append("GENERIC_EXECUTE")
        if access_mask & 0x40000000:  # GENERIC_WRITE
            permissions.append("GENERIC_WRITE")
        if access_mask & 0x80000000:  # GENERIC_READ
            permissions.append("GENERIC_READ")
        
        # Active Directory specific rights
        if access_mask & 0x00000001:  # ADS_RIGHT_DS_CREATE_CHILD
            permissions.append("CREATE_CHILD")
        if access_mask & 0x00000002:  # ADS_RIGHT_DS_DELETE_CHILD
            permissions.append("DELETE_CHILD")
        if access_mask & 0x00000004:  # ADS_RIGHT_ACTRL_DS_LIST
            permissions.append("LIST_CONTENTS")
        if access_mask & 0x00000008:  # ADS_RIGHT_DS_SELF
            permissions.append("SELF_WRITE")
        if access_mask & 0x00000010:  # ADS_RIGHT_DS_READ_PROP
            permissions.append("READ_PROPERTY")
        if access_mask & 0x00000020:  # ADS_RIGHT_DS_WRITE_PROP
            permissions.append("WRITE_PROPERTY")
        if access_mask & 0x00000040:  # ADS_RIGHT_DS_DELETE_TREE
            permissions.append("DELETE_TREE")
        if access_mask & 0x00000080:  # ADS_RIGHT_DS_LIST_OBJECT
            permissions.append("LIST_OBJECT")
        if access_mask & 0x00000100:  # ADS_RIGHT_DS_CONTROL_ACCESS
            permissions.append("CONTROL_ACCESS")
        
        # Full control
        if access_mask & 0x000F01FF == 0x000F01FF:  # Full control for AD objects
            permissions.append("FULL_CONTROL")
        
        return permissions if permissions else [f"RAW_0x{access_mask:08X}"]
    
    def _parse_ace_flags(self, ace_flags: int) -> List[str]:
        """Parse ACE flags into readable strings."""
        flags = []
        
        if ace_flags & 0x01:  # OBJECT_INHERIT_ACE
            flags.append("OBJECT_INHERIT")
        if ace_flags & 0x02:  # CONTAINER_INHERIT_ACE
            flags.append("CONTAINER_INHERIT")
        if ace_flags & 0x04:  # NO_PROPAGATE_INHERIT_ACE
            flags.append("NO_PROPAGATE_INHERIT")
        if ace_flags & 0x08:  # INHERIT_ONLY_ACE
            flags.append("INHERIT_ONLY")
        if ace_flags & 0x10:  # INHERITED_ACE
            flags.append("INHERITED")
        if ace_flags & 0x40:  # SUCCESSFUL_ACCESS_ACE_FLAG
            flags.append("SUCCESSFUL_ACCESS")
        if ace_flags & 0x80:  # FAILED_ACCESS_ACE_FLAG
            flags.append("FAILED_ACCESS")
        
        return flags
    
    def _determine_principal_type(self, sid: str) -> str:
        """Determine the type of principal based on SID patterns."""
        if not sid:
            return "unknown"
        
        # Well-known SIDs
        well_known_sids = {
            "S-1-0": "NULL",
            "S-1-1": "WORLD",
            "S-1-2": "LOCAL",
            "S-1-3": "CREATOR",
            "S-1-4": "NON_UNIQUE",
            "S-1-5": "NT_AUTHORITY",
        }
        
        for prefix, type_name in well_known_sids.items():
            if sid.startswith(prefix):
                if sid.startswith("S-1-5-21-") and sid.endswith("-500"):
                    return "BUILTIN_ADMIN"
                elif sid.startswith("S-1-5-21-") and sid.endswith("-501"):
                    return "BUILTIN_GUEST"
                elif sid.startswith("S-1-5-21-") and sid.endswith("-512"):
                    return "DOMAIN_ADMINS"
                elif sid.startswith("S-1-5-21-") and sid.endswith("-513"):
                    return "DOMAIN_USERS"
                elif sid.startswith("S-1-5-21-") and sid.endswith("-515"):
                    return "DOMAIN_COMPUTERS"
                elif sid.startswith("S-1-5-21-"):
                    # Domain SID - could be user, group, or computer
                    # We'd need to query AD to determine the exact type
                    return "DOMAIN_PRINCIPAL"
                return type_name
        
        return "PRINCIPAL"
    
    def _resolve_sid_to_object_id(self, sid: str) -> Optional[str]:
        """Resolve a SID to the corresponding object's GUID."""
        if not sid:
            return None
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to find the object by SID
            # The objectSid attribute stores the binary SID
            search_filter = f"(objectSid={sid})"
            
            # We only need the objectGUID
            attributes = ['objectGUID']
            
            # Perform the LDAP search
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes,
                size_limit=1  # We only expect one result
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'objectGUID') and entry.objectGUID:
                    return self._strip_guid_parents(str(entry.objectGUID))
            
            # If direct search fails, try alternative approach for well-known SIDs
            # Some well-known SIDs might not be found in the domain DN
            if sid.startswith("S-1-5-") and not sid.startswith("S-1-5-21-"):
                # This is likely a built-in account/group
                # Try searching in the built-in container
                builtin_search_bases = [
                    f"CN=Builtin,{search_base}",
                    f"CN=Users,{search_base}",
                    search_base  # Fallback to domain root
                ]
                
                for base in builtin_search_bases:
                    try:
                        success = self._conn.search(
                            search_base=base,
                            search_filter=search_filter,
                            search_scope=SUBTREE,
                            attributes=attributes,
                            size_limit=1
                        )
                        
                        if success and self._conn.entries:
                            entry = self._conn.entries[0]
                            if hasattr(entry, 'objectGUID') and entry.objectGUID:
                                return self._strip_guid_parents(str(entry.objectGUID))
                    except Exception:
                        continue
            
            # Log debug info for unresolved SIDs
            self.logger.debug(f"Could not resolve SID to object GUID: {sid}")
            return None
            
        except Exception as e:
            self.logger.debug(f"Error resolving SID {sid} to object GUID: {str(e)}")
            return None