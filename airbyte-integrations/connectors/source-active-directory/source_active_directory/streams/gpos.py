from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream


class GPOs(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "gpos"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "GPO's unique objectGUID identifier"},
                "name": {"type": ["string", "null"], "description": "GPO display name"},
                "dn": {"type": ["string", "null"], "description": "Distinguished name of the GPO"},
                "flags": {"type": ["integer", "null"], "description": "GPO flags (enabled/disabled status)"},
                "version_number": {"type": ["integer", "null"], "description": "GPO version number"},
                "functionality_version": {"type": ["integer", "null"], "description": "GPO functionality version"},
                "file_sys_path": {"type": ["string", "null"], "description": "File system path to GPO files"},
                "machine_extension_names": {"type": ["array"], "items": {"type": "string"}, "description": "Machine extension GUIDs"},
                "user_extension_names": {"type": ["array"], "items": {"type": "string"}, "description": "User extension GUIDs"},
                "wql_filter": {"type": ["string", "null"], "description": "WMI filter for GPO"},
                "created_at": {"type": ["string", "null"], "description": "GPO creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Last modification time"},
                # Remote scanning suitable fields
                "machine_extensions_decoded": {"type": ["array"], "items": {"type": "object"}, "description": "Decoded machine extension information"},
                "user_extensions_decoded": {"type": ["array"], "items": {"type": "object"}, "description": "Decoded user extension information"},
                "gpo_status": {"type": ["object", "null"], "description": "Parsed GPO status and flags"},
                "version_info": {"type": ["object", "null"], "description": "Detailed version information breakdown"},
                "wmi_filters_content": {"type": ["array"], "items": {"type": "object"}, "description": "WMI filter details retrieved from LDAP"},
                "remote_analysis": {"type": ["object", "null"], "description": "Remote scanning metadata and capabilities"},
                # Placeholder fields for potential future file access
                "gpt_ini_content": {"type": ["object", "null"], "description": "GPT.INI file content (if accessible)"},
                "machine_registry_content": {"type": ["object", "null"], "description": "Machine Registry.pol content (if accessible)"},
                "user_registry_content": {"type": ["object", "null"], "description": "User Registry.pol content (if accessible)"},
                "machine_scripts": {"type": ["array"], "items": {"type": "object"}, "description": "Machine startup/shutdown scripts (if accessible)"},
                "user_scripts": {"type": ["array"], "items": {"type": "object"}, "description": "User logon/logoff scripts (if accessible)"},
                "security_settings": {"type": ["object", "null"], "description": "Security settings from GptTmpl.inf (if accessible)"},
                "administrative_templates": {"type": ["object", "null"], "description": "Administrative template settings (if accessible)"},
                "folder_redirection": {"type": ["object", "null"], "description": "Folder redirection settings (if accessible)"},
                "software_installation": {"type": ["array"], "items": {"type": "object"}, "description": "Software installation packages (if accessible)"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read Group Policy Objects from Active Directory using LDAP search."""
        
        try:
            # Define the search base - GPOs are stored in CN=Policies,CN=System,<domain>
            domain_dn = self._conn.server.info.other.get('defaultNamingContext', [''])[0]
            search_base = f"CN=Policies,CN=System,{domain_dn}"
            
            # LDAP filter to get Group Policy Container objects
            search_filter = "(objectClass=groupPolicyContainer)"
            
            # Attributes to retrieve for each GPO
            attributes = [
                'objectGUID',               # Unique identifier
                'displayName',              # GPO display name
                'distinguishedName',        # DN of the GPO
                'flags',                    # GPO flags (enabled/disabled)
                'versionNumber',            # GPO version number
                'gPCFunctionalityVersion',  # GPO functionality version
                'gPCFileSysPath',           # File system path
                'gPCMachineExtensionNames', # Machine extensions
                'gPCUserExtensionNames',    # User extensions
                'gPCWQLFilter',             # WMI filter
                'whenCreated',              # Creation time
                'whenChanged',              # Last modified time
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
            
            # Process each GPO entry
            for entry in self._conn.entries:
                # Extract objectGUID as the primary ID
                object_guid = entry.objectGUID
                if not object_guid:
                    raise ValueError(f"GPO entry missing objectGUID: {entry.entry_dn}")

                # Parse machine extension names
                machine_extensions = []
                if hasattr(entry, 'gPCMachineExtensionNames') and entry.gPCMachineExtensionNames:
                    machine_extensions = self._parse_extension_names(str(entry.gPCMachineExtensionNames))
                
                # Parse user extension names
                user_extensions = []
                if hasattr(entry, 'gPCUserExtensionNames') and entry.gPCUserExtensionNames:
                    user_extensions = self._parse_extension_names(str(entry.gPCUserExtensionNames))
                
                # Get additional GPO information suitable for remote scanning
                gpo_content = self._get_remote_gpo_info(entry)
                
                # Build the GPO record
                gpo_record = {
                    "id": self._strip_guid_parents(str(object_guid.value)),
                    "name": str(entry.displayName.value) if entry.displayName else None,
                    "dn": str(entry.distinguishedName.value) if entry.distinguishedName else None,
                    "flags": int(entry.flags.value) if entry.flags else None,
                    "version_number": int(entry.versionNumber.value) if entry.versionNumber else None,
                    "functionality_version": int(entry.gPCFunctionalityVersion.value) if entry.gPCFunctionalityVersion else None,
                    "file_sys_path": str(entry.gPCFileSysPath.value) if entry.gPCFileSysPath else None,
                    "machine_extension_names": machine_extensions,
                    "user_extension_names": user_extensions,
                    "wql_filter": str(entry.gPCWQLFilter.value) if entry.gPCWQLFilter else None,
                    "created_at": str(entry.whenCreated.value) if entry.whenCreated else None,
                    "modified_at": str(entry.whenChanged.value) if entry.whenChanged else None,
                    # Add remote-accessible GPO information
                    **gpo_content
                }
                
                yield gpo_record
                    
        except Exception as e:
            self.logger.error(f"Error during LDAP search for GPOs: {str(e)}")
            raise
    
    def _parse_extension_names(self, extension_string: str) -> list:
        """Parse GPO extension names from the stored format."""
        if not extension_string:
            return []
        
        # Extension names are stored in format like: [{GUID}{GUID}][{GUID}{GUID}]...
        # Each pair represents Tool GUID and Snap-in GUID
        extensions = []
        
        # Remove square brackets and split by ][
        if extension_string.startswith('[') and extension_string.endswith(']'):
            extension_string = extension_string[1:-1]  # Remove outer brackets
            
            # Split by '][' to get individual extension pairs
            extension_pairs = extension_string.split('][')
            
            for pair in extension_pairs:
                if pair:
                    # Each pair should contain two GUIDs: {GUID}{GUID}
                    # Split by }{ to separate them
                    if '}{' in pair:
                        guids = pair.split('}{')
                        if len(guids) == 2:
                            tool_guid = guids[0].strip('{}')
                            snapin_guid = guids[1].strip('{}')
                            extensions.append(f"{tool_guid}:{snapin_guid}")
                    else:
                        # Single GUID in the pair
                        guid = pair.strip('{}')
                        if guid:
                            extensions.append(guid)
        
        return extensions

    def _get_remote_gpo_info(self, entry) -> dict:
        """Get additional GPO information available through LDAP for remote scanning."""
        content = {
            "gpt_ini_content": None,
            "machine_registry_content": None,
            "user_registry_content": None,
            "machine_scripts": [],
            "user_scripts": [],
            "security_settings": None,
            "administrative_templates": None,
            "wmi_filters_content": [],
            "folder_redirection": None,
            "software_installation": [],
        }
        
        try:
            # Decode extension information for better analysis
            content["machine_extensions_decoded"] = self._decode_extension_names(
                str(entry.gPCMachineExtensionNames) if hasattr(entry, 'gPCMachineExtensionNames') and entry.gPCMachineExtensionNames else None
            )
            content["user_extensions_decoded"] = self._decode_extension_names(
                str(entry.gPCUserExtensionNames) if hasattr(entry, 'gPCUserExtensionNames') and entry.gPCUserExtensionNames else None
            )
            
            # Parse GPO flags for detailed status
            content["gpo_status"] = self._parse_gpo_flags(
                int(entry.flags.value) if hasattr(entry, 'flags') and entry.flags else 0
            )
            
            # Get version breakdown
            content["version_info"] = self._parse_version_number(
                int(entry.versionNumber.value) if hasattr(entry, 'versionNumber') and entry.versionNumber else 0
            )
            
            # Try to get WMI filter details if reference exists
            if hasattr(entry, 'gPCWQLFilter') and entry.gPCWQLFilter:
                content["wmi_filters_content"] = self._get_wmi_filter_details(str(entry.gPCWQLFilter.value))
            
            # Add remote accessibility info
            content["remote_analysis"] = {
                "sysvol_path_available": bool(hasattr(entry, 'gPCFileSysPath') and entry.gPCFileSysPath),
                "sysvol_path": str(entry.gPCFileSysPath.value) if hasattr(entry, 'gPCFileSysPath') and entry.gPCFileSysPath else None,
                "extensions_count": {
                    "machine": len(content["machine_extensions_decoded"]),
                    "user": len(content["user_extensions_decoded"])
                },
                "scan_method": "remote_ldap_only",
                "file_access_available": False
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting remote GPO info: {str(e)}")
            
        return content
    
    def _decode_extension_names(self, extension_string: Optional[str]) -> list:
        """Decode GPO extension GUIDs to human-readable names where possible."""
        if not extension_string:
            return []
        
        # Common GPO extension GUIDs and their meanings
        EXTENSION_GUID_MAP = {
            # Administrative Templates
            "35378EAC-683F-11D2-A89A-00C04FBBCFA2": "Administrative Templates (Registry)",
            
            # Security Settings
            "827D319E-6EAC-11D2-A4EA-00C04F79F83A": "Security Settings",
            "803E14A0-B4FB-11D0-A0D0-00A0C90F574B": "Security Settings - Local Users and Groups",
            
            # Scripts
            "42B5FAAE-6536-11D2-AE5A-0000F87571E3": "Scripts (Startup/Shutdown)",
            "40B6664F-4972-11D1-A7CA-0000F87571E3": "Scripts (Logon/Logoff)",
            
            # Software Installation
            "C6DC5466-785A-11D2-84D0-00C04FB169F7": "Software Installation (Computers)",
            "942A8E4F-A261-11D1-A760-00C04FB9603F": "Software Installation (Users)",
            
            # Folder Redirection
            "25537BA6-77A8-11D2-9B6C-0000F8080861": "Folder Redirection",
            
            # Internet Explorer
            "A2E30F80-D7DE-11d2-BBDE-00C04F86AE3B": "Internet Explorer Branding",
            "3A0DBA37-F8B2-4356-83DE-3E90BD5C261F": "Internet Explorer User Accelerators",
            
            # Windows Components
            "0E28E245-9368-4853-AD84-6DA3BA35BB75": "Group Policy Environment",
            "17D89FEC-5C44-4972-B12D-241CAEF74509": "Group Policy Local Users and Groups",
            
            # Preferences Extensions
            "91FBB303-0CD5-4055-BF42-E512A681B325": "Group Policy Preferences - Services",
            "A3F3E02B-B83D-4C73-9038-AE81B5763F7D": "Group Policy Preferences - Files",
            "E62688F0-25FD-4c90-BFF5-F508B9D2E31F": "Group Policy Preferences - Folders",
            "F9C77450-3A41-477E-9310-9ACD617BD9E3": "Group Policy Preferences - Environment Variables",
            "E5094040-C46C-4115-B030-04FB2E545B00": "Group Policy Preferences - Regional Options",
        }
        
        extensions = []
        parsed_guids = self._parse_extension_names(extension_string)
        
        for guid_pair in parsed_guids:
            if ':' in guid_pair:
                tool_guid, snapin_guid = guid_pair.split(':', 1)
            else:
                tool_guid = guid_pair
                snapin_guid = None
            
            # Look up the extension name
            extension_name = EXTENSION_GUID_MAP.get(tool_guid.upper(), f"Unknown Extension ({tool_guid})")
            
            extension_info = {
                "tool_guid": tool_guid,
                "snapin_guid": snapin_guid,
                "extension_name": extension_name,
                "category": self._categorize_extension(tool_guid.upper())
            }
            extensions.append(extension_info)
        
        return extensions
    
    def _categorize_extension(self, guid: str) -> str:
        """Categorize GPO extensions by type."""
        categories = {
            "35378EAC-683F-11D2-A89A-00C04FBBCFA2": "administrative_templates",
            "827D319E-6EAC-11D2-A4EA-00C04F79F83A": "security",
            "803E14A0-B4FB-11D0-A0D0-00A0C90F574B": "security",
            "42B5FAAE-6536-11D2-AE5A-0000F87571E3": "scripts",
            "40B6664F-4972-11D1-A7CA-0000F87571E3": "scripts",
            "C6DC5466-785A-11D2-84D0-00C04FB169F7": "software_installation",
            "942A8E4F-A261-11D1-A760-00C04FB9603F": "software_installation",
            "25537BA6-77A8-11D2-9B6C-0000F8080861": "folder_redirection",
        }
        return categories.get(guid, "other")
    
    def _parse_gpo_flags(self, flags: int) -> dict:
        """Parse GPO flags to determine status."""
        return {
            "user_disabled": bool(flags & 0x00000001),
            "computer_disabled": bool(flags & 0x00000002),
            "user_enabled": not bool(flags & 0x00000001),
            "computer_enabled": not bool(flags & 0x00000002),
            "raw_flags": flags,
            "status_summary": self._get_gpo_status_summary(flags)
        }
    
    def _get_gpo_status_summary(self, flags: int) -> str:
        """Get human-readable GPO status."""
        user_disabled = bool(flags & 0x00000001)
        computer_disabled = bool(flags & 0x00000002)
        
        if user_disabled and computer_disabled:
            return "All settings disabled"
        elif user_disabled:
            return "User configuration disabled"
        elif computer_disabled:
            return "Computer configuration disabled"
        else:
            return "Enabled"
    
    def _parse_version_number(self, version: int) -> dict:
        """Parse GPO version number into components."""
        # Version number format: high 16 bits = computer version, low 16 bits = user version
        computer_version = (version >> 16) & 0xFFFF
        user_version = version & 0xFFFF
        
        return {
            "full_version": version,
            "computer_version": computer_version,
            "user_version": user_version,
            "has_computer_settings": computer_version > 0,
            "has_user_settings": user_version > 0
        }
    
    def _get_wmi_filter_details(self, wmi_filter_dn: str) -> list:
        """Try to get WMI filter details from DN."""
        filters = []
        if not wmi_filter_dn:
            return filters
        
        try:
            # Search for the WMI filter object
            success = self._conn.search(
                search_base=wmi_filter_dn,
                search_filter="(objectClass=msWMI-Som)",
                search_scope='BASE',
                attributes=['msWMI-Name', 'msWMI-Parm1', 'msWMI-Parm2', 'msWMI-Author']
            )
            
            if success and self._conn.entries:
                filter_entry = self._conn.entries[0]
                filter_info = {
                    "dn": wmi_filter_dn,
                    "name": str(filter_entry['msWMI-Name'].value) if filter_entry['msWMI-Name'] else None,
                    "description": str(filter_entry['msWMI-Parm1'].value) if filter_entry['msWMI-Parm1'] else None,
                    "query": str(filter_entry['msWMI-Parm2'].value) if filter_entry['msWMI-Parm2'] else None,
                    "author": str(filter_entry['msWMI-Author'].value) if filter_entry['msWMI-Author'] else None
                }
                filters.append(filter_info)
        except Exception as e:
            self.logger.warning(f"Error getting WMI filter details: {str(e)}")
            filters.append({
                "dn": wmi_filter_dn,
                "error": f"Could not retrieve filter details: {str(e)}"
            })
        
        return filters