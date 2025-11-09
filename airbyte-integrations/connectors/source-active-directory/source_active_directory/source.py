import logging
import ssl

from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import AbstractSource
from airbyte_cdk.sources.streams import Stream

from ldap3 import Connection, Server, ALL, SIMPLE, Tls

from .streams import (
    ACLs,
    Computers,
    Domains,
    Forest,
    ForestDomains,
    GPOs,
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
            ACLs(conn=self._get_ldap_connection(config)),
            Computers(conn=self._get_ldap_connection(config)),
            Forest(conn=self._get_ldap_connection(config)),
            Domains(conn=self._get_ldap_connection(config)),
            ForestDomains(conn=self._get_ldap_connection(config)),
            GPOs(conn=self._get_ldap_connection(config)),
            Sites(conn=self._get_ldap_connection(config)),
            OrganizationalUnits(conn=self._get_ldap_connection(config)),
            Users(conn=self._get_ldap_connection(config)),
            Groups(conn=self._get_ldap_connection(config)),
            GroupMemberships(conn=self._get_ldap_connection(config)),
            OrganizationalUnitObjects(conn=self._get_ldap_connection(config)),
        ]

    def _get_ldap_connection(self, config: Mapping[str, Any]) -> Connection:
        username = config['username']
        password = config['password']
        domain = config['domain']
        domain_ip = config['domain_ip']

        user_dn = f"{username}@{domain}"

        try:
            # Try LDAPS first
            tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
            server = Server(f'ldaps://{domain_ip}', port=636, use_ssl=True, get_info=ALL, tls=tls_config)
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True,
                authentication=SIMPLE
            )

        except Exception as e:
            logging.warning(f"LDAPS connection failed: {e}")
            # Try LDAP (non-SSL)
            server = Server(f'ldap://{domain_ip}',use_ssl=False, get_info=ALL)
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                auto_bind=True
            )
            
        return conn
