from typing import Any, Iterable, Mapping, Optional

from ldap3 import SUBTREE

from .base import ActiveDirectoryStream
from .organizational_units import OrganizationalUnits


class OrganizationalUnitObjects(ActiveDirectoryStream):
    @property
    def name(self) -> str:
        return "organizational_unit_objects"
    
    @property
    def primary_key(self) -> Optional[str]:
        return "id"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["string"], "description": "Unique relationship identifier"},
                "ou_id": {"type": ["string"], "description": "OU's unique objectGUID identifier"},
                "ou_name": {"type": ["string"], "description": "OU name"},
                "ou_distinguished_name": {"type": ["string"], "description": "OU distinguished name"},
                "object_id": {"type": ["string"], "description": "Object's unique objectGUID identifier"},
                "object_type": {"type": ["string"], "description": "Type of object (user, group, computer, etc.)"},
                "object_name": {"type": ["string"], "description": "Object name"},
                "object_distinguished_name": {"type": ["string"], "description": "Object distinguished name"},
                "object_sam_account_name": {"type": ["string", "null"], "description": "Object SAM account name"},
                "is_direct_child": {"type": ["boolean"], "description": "Whether the object is directly under this OU"},
                "created_at": {"type": ["string", "null"], "description": "Object creation time"},
                "modified_at": {"type": ["string", "null"], "description": "Object last modification time"},
            }
        }
    
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read organizational unit to object relationships from Active Directory."""
        
        try:
            # Get all OUs using the existing organizational_units stream
            ous_stream = OrganizationalUnits(conn=self._conn)
            
            for ou in ous_stream.read_records(sync_mode):
                try:
                    # Get all objects directly under this OU
                    objects = self._get_ou_objects(ou['distinguished_name'])
                    
                    for obj in objects:
                        try:
                            relationship_id = f"{ou['id']}_{obj['id']}"
                            
                            # Check if object is directly under this OU
                            is_direct_child = self._is_direct_child(obj['distinguished_name'], ou['distinguished_name'])
                            
                            ou_object_record = {
                                "id": relationship_id,
                                "ou_id": ou["id"],
                                "ou_name": ou["name"],
                                "ou_distinguished_name": ou["distinguished_name"],
                                "object_id": obj["id"],
                                "object_type": obj["type"],
                                "object_name": obj["name"],
                                "object_distinguished_name": obj["distinguished_name"],
                                "object_sam_account_name": obj["sam_account_name"],
                                "is_direct_child": is_direct_child,
                                "created_at": obj["created_at"],
                                "modified_at": obj["modified_at"],
                            }
                            
                            yield ou_object_record
                            
                        except Exception as e:
                            self.logger.warning(f"Error processing OU-object relationship: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error processing OU {ou['name']}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error during organizational unit objects search: {str(e)}")
            raise
    
    def _get_ou_objects(self, ou_dn: str) -> list:
        """Get all objects (users, groups, computers, etc.) under an OU."""
        try:
            # Search for common AD object types
            search_filter = "(|(objectClass=user)(objectClass=group)(objectClass=computer)(objectClass=organizationalUnit))"
            
            attributes = [
                'objectGUID',
                'objectClass',
                'name',
                'distinguishedName',
                'sAMAccountName',
                'whenCreated',
                'whenChanged'
            ]
            
            success = self._conn.search(
                search_base=ou_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            objects = []
            if success:
                for entry in self._conn.entries:
                    try:
                        if hasattr(entry, 'objectGUID') and entry.objectGUID:
                            # Skip the OU itself
                            if str(entry.distinguishedName.value) == ou_dn:
                                continue
                            
                            # Determine object type from objectClass
                            object_type = self._determine_object_type(entry.objectClass.values if hasattr(entry, 'objectClass') else [])
                            
                            obj = {
                                "id": self._strip_guid_parents(entry.objectGUID.value),
                                "type": object_type,
                                "name": str(entry.name.value) if hasattr(entry, 'name') and entry.name else None,
                                "distinguished_name": str(entry.distinguishedName.value) if hasattr(entry, 'distinguishedName') and entry.distinguishedName else None,
                                "sam_account_name": str(entry.sAMAccountName.value) if hasattr(entry, 'sAMAccountName') and entry.sAMAccountName else None,
                                "created_at": str(entry.whenCreated.value) if hasattr(entry, 'whenCreated') and entry.whenCreated else None,
                                "modified_at": str(entry.whenChanged.value) if hasattr(entry, 'whenChanged') and entry.whenChanged else None,
                            }
                            objects.append(obj)
                    except Exception as e:
                        self.logger.warning(f"Error processing object entry: {str(e)}")
                        continue
            return objects
        except Exception:
            return []
    
    def _determine_object_type(self, object_classes: list) -> str:
        """Determine the primary object type from objectClass values."""
        if not object_classes:
            return "unknown"
        
        # Priority order for determining type
        type_priorities = {
            "user": ["user"],
            "group": ["group"],
            "computer": ["computer"],
            "organizational_unit": ["organizationalUnit"],
            "contact": ["contact"],
            "printer": ["printQueue"],
            "shared_folder": ["volume"],
        }
        
        object_classes_lower = [oc.lower() for oc in object_classes]
        
        for obj_type, class_names in type_priorities.items():
            if any(cls.lower() in object_classes_lower for cls in class_names):
                return obj_type
        
        return "other"
    
    def _is_direct_child(self, object_dn: str, ou_dn: str) -> bool:
        """Check if an object is a direct child of the OU (not nested in sub-OUs)."""
        try:
            # Remove the OU DN from the object DN
            relative_dn = object_dn.replace(f",{ou_dn}", "")
            
            # If there are no commas in the relative DN, it's a direct child
            return ',' not in relative_dn
        except Exception:
            return False
