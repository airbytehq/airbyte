import struct

from typing import Any, Iterable, Mapping, Optional, List, Dict

from ldap3 import SUBTREE
from ldap3.protocol.microsoft import security_descriptor_control

from .base import ActiveDirectoryStream


class ACLs(ActiveDirectoryStream):
    """Stream for extracting Access Control Lists (ACLs) from Active Directory objects."""
    
    def __init__(self, conn):
        """Initialize the ACLs stream with SID to objectGUID cache."""
        super().__init__(conn)
        self._sid_to_guid_cache: dict[str, str] = {}
    
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
            # We'll build the SID cache as we scan objects, since we're already retrieving their SIDs
            self.logger.info("Starting comprehensive ACL scan for all object types with corresponding streams...")
            
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            search_filter = "(objectClass=*)"
            
            # Attributes to retrieve for each object
            attributes = [
                'objectGUID',           # Unique identifier
                'distinguishedName',    # DN
                'objectClass',          # Object type
                'objectSid',            # Security identifier
                'nTSecurityDescriptor', # Security descriptor
                'whenCreated',          # Creation time
                'whenChanged',          # Last modified time
            ]
            

            sd_control = security_descriptor_control(sdflags=7)  # 1+2+4

            # Perform the LDAP search
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes,
                controls=sd_control
            )
            
            if not success:
                self.logger.error(f"LDAP search failed: {self._conn.result}")
                return
            
            # First pass: Build SID cache from all scanned objects
            self.logger.info("First pass: Building SID cache from scanned objects...")
            all_entries = list(self._conn.entries)  # Store entries for second pass
            
            self._populate_sid_cache(all_entries)

            self.logger.info(f"SID cache built with {len(self._sid_to_guid_cache)} entries")
            self.logger.info(f"Total objects found: {len(all_entries)}")
            
            # Second pass: Process ACLs and extract owner/group SIDs from security descriptors
            self.logger.info("Second pass: Processing ACLs...")
            
            # Process each object entry for ACLs
            for entry in all_entries:
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
                    acl_entries, owner_sid, group_sid = self._parse_security_descriptor(security_descriptor)
                    
                    # Add owner and group SIDs to cache if we can resolve them quickly
                    if owner_sid and owner_sid not in self._sid_to_guid_cache:
                        owner_guid = self._quick_resolve_sid(owner_sid)
                        if owner_guid:
                            self._sid_to_guid_cache[owner_sid] = owner_guid
                    
                    if group_sid and group_sid not in self._sid_to_guid_cache:
                        group_guid = self._quick_resolve_sid(group_sid)
                        if group_guid:
                            self._sid_to_guid_cache[group_sid] = group_guid
                    
                    # Generate ACL records for each ACE
                    for ace_info in acl_entries:
                        # Get principal object ID from cache
                        principal_object_id = self._sid_to_guid_cache.get(ace_info['principal_sid'])

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
    
    def _populate_sid_cache(self, entries: List[Any]) -> None:
        """Populate the SID to objectGUID cache from a list of LDAP entries."""
        for entry in entries:
            if hasattr(entry, 'objectGUID') and hasattr(entry, 'objectSid'):
                try:
                    object_guid = entry.objectGUID
                    object_sid = entry.objectSid
                    
                    if object_guid and object_sid:
                        sid_string = self._convert_binary_sid_to_string(object_sid.raw_values[0])
                        if sid_string:
                            resource_id = self._strip_guid_parents(str(object_guid.value))
                            self._sid_to_guid_cache[sid_string] = resource_id
                except Exception as e:
                    self.logger.debug(f"Error adding SID to cache: {str(e)}")
                    continue
            
    def _get_primary_object_class(self, object_classes: List[str]) -> str:
        """Determine the primary object class from a list of object classes."""
        # Priority order for determining primary class - matches our available streams
        priority_classes = [
            # Core identity objects (highest priority)
            'user', 'group', 'computer', 'contact',
            
            # Organizational structure
            'organizationalUnit', 'container', 'domain', 'domainDNS',
            
            # Group Policy objects
            'groupPolicyContainer',
            
            # Network topology
            'site', 'subnet', 'siteLink',
            
            # Service accounts and special principals
            'msDS-GroupManagedServiceAccount', 'foreignSecurityPrincipal',
            
            # Infrastructure objects
            'configuration', 'crossRef', 'serviceConnectionPoint',
            
            # Security and certificates
            'trustedDomain', 'ntAuthStore', 'pKICertificateTemplate',
            
            # Fallback for common containers
            'organizationalPerson', 'person', 'top'
        ]
        
        for priority_class in priority_classes:
            if priority_class in object_classes:
                return priority_class
        
        # Return the last (most specific) class if no priority match
        return object_classes[-1] if object_classes else 'unknown'
    
    def _parse_security_descriptor(self, security_descriptor_bytes: bytes) -> tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
        """Parse a binary security descriptor to extract ACL information and owner/group SIDs."""
        try:
            # Security descriptor structure according to Microsoft documentation
            # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/7d4dac05-9cef-4563-a058-f108abecce1d
            
            if len(security_descriptor_bytes) < 20:
                self.logger.warning("Security descriptor too short")
                return [], None, None
            
            # Parse security descriptor header
            revision = security_descriptor_bytes[0]
            control_flags = struct.unpack('<H', security_descriptor_bytes[2:4])[0]
            
            # Extract offsets
            owner_offset = struct.unpack('<L', security_descriptor_bytes[4:8])[0]
            group_offset = struct.unpack('<L', security_descriptor_bytes[8:12])[0]
            sacl_offset = struct.unpack('<L', security_descriptor_bytes[12:16])[0]
            dacl_offset = struct.unpack('<L', security_descriptor_bytes[16:20])[0]
            
            acl_entries = []
            owner_sid = None
            group_sid = None
            
            # Parse owner SID if present
            if owner_offset > 0 and owner_offset < len(security_descriptor_bytes):
                try:
                    owner_sid = self._parse_sid_at_offset(security_descriptor_bytes, owner_offset)
                except Exception as e:
                    self.logger.debug(f"Error parsing owner SID: {str(e)}")
            
            # Parse group SID if present
            if group_offset > 0 and group_offset < len(security_descriptor_bytes):
                try:
                    group_sid = self._parse_sid_at_offset(security_descriptor_bytes, group_offset)
                except Exception as e:
                    self.logger.debug(f"Error parsing group SID: {str(e)}")
            
            # Parse DACL (Discretionary Access Control List) if present
            if dacl_offset > 0 and dacl_offset < len(security_descriptor_bytes):
                dacl_entries = self._parse_acl(security_descriptor_bytes, dacl_offset, "DACL")
                acl_entries.extend(dacl_entries)
            
            # Parse SACL (System Access Control List) if present
            if sacl_offset > 0 and sacl_offset < len(security_descriptor_bytes):
                sacl_entries = self._parse_acl(security_descriptor_bytes, sacl_offset, "SACL")
                acl_entries.extend(sacl_entries)
            
            return acl_entries, owner_sid, group_sid
            
        except Exception as e:
            self.logger.warning(f"Error parsing security descriptor: {str(e)}")
            return [], None, None
    
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
        
        # Check for well-known domain RIDs
        domain_rids = {
            "-500": "BUILTIN_ADMIN",
            "-501": "BUILTIN_GUEST", 
            "-502": "KRBTGT",
            "-512": "DOMAIN_ADMINS",
            "-513": "DOMAIN_USERS",
            "-514": "DOMAIN_GUESTS", 
            "-515": "DOMAIN_COMPUTERS",
            "-516": "DOMAIN_CONTROLLERS",
            "-517": "CERT_PUBLISHERS",
            "-518": "SCHEMA_ADMINS",
            "-519": "ENTERPRISE_ADMINS",
            "-520": "GROUP_POLICY_CREATOR_OWNERS",
            "-521": "READONLY_DOMAIN_CONTROLLERS",
            "-522": "CLONEABLE_DOMAIN_CONTROLLERS",
            "-525": "PROTECTED_USERS",
            "-526": "KEY_ADMINS",
            "-527": "ENTERPRISE_KEY_ADMINS",
        }
        
        # Check for specific NT AUTHORITY SIDs
        nt_authority_sids = {
            "S-1-5-1": "DIALUP",
            "S-1-5-2": "NETWORK", 
            "S-1-5-3": "BATCH",
            "S-1-5-4": "INTERACTIVE",
            "S-1-5-6": "SERVICE",
            "S-1-5-7": "ANONYMOUS",
            "S-1-5-8": "PROXY",
            "S-1-5-9": "ENTERPRISE_DOMAIN_CONTROLLERS",
            "S-1-5-10": "PRINCIPAL_SELF",
            "S-1-5-11": "AUTHENTICATED_USERS",
            "S-1-5-12": "RESTRICTED_CODE",
            "S-1-5-13": "TERMINAL_SERVER_USERS",
            "S-1-5-14": "REMOTE_INTERACTIVE_LOGON",
            "S-1-5-15": "THIS_ORGANIZATION",
            "S-1-5-17": "IUSR",
            "S-1-5-18": "LOCAL_SYSTEM",
            "S-1-5-19": "LOCAL_SERVICE",
            "S-1-5-20": "NETWORK_SERVICE",
            "S-1-5-32": "BUILTIN",
        }
        
        # Check exact matches first
        if sid in nt_authority_sids:
            return nt_authority_sids[sid]
        
        # Check for domain RIDs
        if sid.startswith("S-1-5-21-"):
            for rid_suffix, principal_type in domain_rids.items():
                if sid.endswith(rid_suffix):
                    return principal_type
            # Generic domain principal
            return "DOMAIN_PRINCIPAL"
        
        # Check for BUILTIN domain (S-1-5-32)
        if sid.startswith("S-1-5-32-"):
            builtin_rids = {
                "-544": "BUILTIN_ADMINISTRATORS",
                "-545": "BUILTIN_USERS", 
                "-546": "BUILTIN_GUESTS",
                "-547": "BUILTIN_POWER_USERS",
                "-548": "BUILTIN_ACCOUNT_OPERATORS",
                "-549": "BUILTIN_SERVER_OPERATORS",
                "-550": "BUILTIN_PRINT_OPERATORS",
                "-551": "BUILTIN_BACKUP_OPERATORS",
                "-552": "BUILTIN_REPLICATOR",
                "-554": "BUILTIN_PRE_WINDOWS_2000_COMPATIBLE_ACCESS",
                "-555": "BUILTIN_REMOTE_DESKTOP_USERS",
                "-556": "BUILTIN_NETWORK_CONFIGURATION_OPERATORS",
                "-557": "BUILTIN_INCOMING_FOREST_TRUST_BUILDERS",
                "-558": "BUILTIN_PERFORMANCE_MONITOR_USERS",
                "-559": "BUILTIN_PERFORMANCE_LOG_USERS",
                "-560": "BUILTIN_WINDOWS_AUTHORIZATION_ACCESS_GROUP",
                "-561": "BUILTIN_TERMINAL_SERVER_LICENSE_SERVERS",
                "-562": "BUILTIN_DISTRIBUTED_COM_USERS",
                "-568": "BUILTIN_IIS_USERS",
                "-569": "BUILTIN_CRYPTOGRAPHIC_OPERATORS",
                "-573": "BUILTIN_EVENT_LOG_READERS",
                "-574": "BUILTIN_CERTIFICATE_SERVICE_DCOM_ACCESS",
            }
            for rid_suffix, principal_type in builtin_rids.items():
                if sid.endswith(rid_suffix):
                    return principal_type
            return "BUILTIN_GROUP"
        
        # Check for well-known SID prefixes
        for prefix, type_name in well_known_sids.items():
            if sid.startswith(prefix):
                return type_name
        
        return "PRINCIPAL"
    
    def _categorize_object_type(self, object_type: str) -> str:
        """Categorize object types into logical groups for reporting."""
        identity_objects = ['user', 'group', 'computer', 'contact', 'msDS-GroupManagedServiceAccount']
        organizational_objects = ['organizationalUnit', 'container', 'domain', 'domainDNS'] 
        policy_objects = ['groupPolicyContainer']
        network_objects = ['site', 'subnet', 'siteLink']
        infrastructure_objects = ['configuration', 'crossRef', 'serviceConnectionPoint', 'trustedDomain']
        security_objects = ['ntAuthStore', 'pKICertificateTemplate', 'foreignSecurityPrincipal']
        
        if object_type in identity_objects:
            return "Identity"
        elif object_type in organizational_objects:
            return "Organizational"
        elif object_type in policy_objects:
            return "Group Policy"
        elif object_type in network_objects:
            return "Network"
        elif object_type in infrastructure_objects:
            return "Infrastructure"
        elif object_type in security_objects:
            return "Security"
        else:
            return "Other"
    
    def _get_stream_mapping(self) -> dict:
        """Return mapping of object types to their corresponding streams."""
        return {
            'user': 'Users',
            'group': 'Groups', 
            'computer': 'Computers',
            'organizationalUnit': 'OrganizationalUnits',
            'groupPolicyContainer': 'GPOs',
            'site': 'Sites',
            'domain': 'Domains',
            'domainDNS': 'Domains',
            'crossRef': 'ForestDomains',
            'contact': 'Users (extended)',
            'container': 'OrganizationalUnits (extended)',
            'msDS-GroupManagedServiceAccount': 'Users (extended)',
            'foreignSecurityPrincipal': 'Groups (extended)',
            'serviceConnectionPoint': 'Infrastructure',
            'trustedDomain': 'Domains (extended)',
            'subnet': 'Sites (extended)',
            'siteLink': 'Sites (extended)',
            'ntAuthStore': 'Security',
            'pKICertificateTemplate': 'Security',
            'configuration': 'Infrastructure',
        }
    
    def _parse_sid_at_offset(self, sd_bytes: bytes, offset: int) -> Optional[str]:
        """Parse a SID at a specific offset in the security descriptor."""
        try:
            if offset >= len(sd_bytes):
                return None
            
            # SID structure starts at the offset
            sid_bytes = sd_bytes[offset:]
            return self._parse_sid(sid_bytes)
            
        except Exception as e:
            self.logger.debug(f"Error parsing SID at offset {offset}: {str(e)}")
            return None
    
    def _quick_resolve_sid(self, sid: str) -> Optional[str]:
        """Quick resolution for SIDs not in cache (typically owner/group SIDs)."""
        if not sid:
            return None
        
        try:
            # Define the search base - typically the domain DN
            search_base = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            
            # LDAP filter to find the object by SID
            search_filter = f"(objectSid={sid})"
            
            # We only need the objectGUID
            attributes = ['objectGUID']
            
            # Perform a quick lookup
            success = self._conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes,
                size_limit=1
            )
            
            if success and self._conn.entries:
                entry = self._conn.entries[0]
                if hasattr(entry, 'objectGUID') and entry.objectGUID:
                    return self._strip_guid_parents(str(entry.objectGUID))
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error resolving SID {sid}: {str(e)}")
            return None
    
    def _convert_binary_sid_to_string(self, binary_sid: bytes) -> Optional[str]:
        """Convert binary SID from objectSid attribute to string format."""
        try:
            if len(binary_sid) < 8:
                return None
            
            revision = binary_sid[0]
            sub_authority_count = binary_sid[1]
            
            if len(binary_sid) < 8 + (sub_authority_count * 4):
                return None
            
            # Parse identifier authority (6 bytes, big-endian)
            identifier_authority = struct.unpack('>Q', b'\x00\x00' + binary_sid[2:8])[0]
            
            # Parse sub-authorities (4 bytes each, little-endian)
            sub_authorities = []
            for i in range(sub_authority_count):
                offset = 8 + (i * 4)
                sub_authority = struct.unpack('<L', binary_sid[offset:offset + 4])[0]
                sub_authorities.append(str(sub_authority))
            
            # Format as standard SID string
            sid_string = f"S-{revision}-{identifier_authority}"
            if sub_authorities:
                sid_string += "-" + "-".join(sub_authorities)
            
            return sid_string
            
        except Exception as e:
            self.logger.debug(f"Error converting binary SID to string: {str(e)}")
            return None