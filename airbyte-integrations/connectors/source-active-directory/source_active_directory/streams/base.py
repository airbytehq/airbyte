from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from ldap3 import Connection

from airbyte_cdk.sources.streams import Stream


class ActiveDirectoryStream(Stream, ABC):
    """Base stream class for Active Directory."""

    def __init__(self, conn: Connection):
        """
        Initialize the stream with an LDAP connection.
        
        :param conn: An established LDAP connection.
        """
        super().__init__()
        self._conn = conn

    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def primary_key(self) -> Optional[str]:
        ...
    
    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        ...

    @abstractmethod
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        ...


    @staticmethod
    def _strip_guid_parents(guid: str) -> str:
        """
        Strip the curly braces from a GUID.
        
        :param guid: The GUID string to be stripped.
        :return: The stripped GUID.
        """
        return guid.strip('{}') if guid else guid