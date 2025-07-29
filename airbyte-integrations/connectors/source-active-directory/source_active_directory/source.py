from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import AbstractSource
from airbyte_cdk.sources.streams import Stream

from bloodhound.ad.authentication import ADAuthentication
from ldap3 import Connection

from .streams import (
    DomainOrganizationalUnits,
    Domains,
    Forest,
    ForestDomains,
    GroupMemberships,
    Groups,
    OrganizationalUnitObjects,
    OrganizationalUnits,
    Sites,
    Users,
)


class SourceActiveDirectory(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            self._get_ldap_connection(config)
            return True, None    

        except Exception as e:
            return False, f"Error connecting to DC: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Forest(conn=self._get_ldap_connection(config)),
            Domains(conn=self._get_ldap_connection(config)),
            ForestDomains(conn=self._get_ldap_connection(config)),
            Sites(conn=self._get_ldap_connection(config)),
            OrganizationalUnits(conn=self._get_ldap_connection(config)),
            DomainOrganizationalUnits(conn=self._get_ldap_connection(config)),
            Users(conn=self._get_ldap_connection(config)),
            Groups(conn=self._get_ldap_connection(config)),
            GroupMemberships(conn=self._get_ldap_connection(config)),
            OrganizationalUnitObjects(conn=self._get_ldap_connection(config)),
        ]

    def _get_ldap_connection(self, config: Mapping[str, Any]) -> Connection:
        username = config['username']
        password = config['password']
        domain = config['domain']

        # Auth object
        auth = ADAuthentication(
            domain=domain,
            username=username,
            password=password,
        )

        domain_ip = config['domain_ip']
        connection = auth.getLDAPConnection(ip=domain_ip, protocol='ldap')
        return connection

