#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional

from airbyte_cdk.sources.file_based import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class AbstractFileBasedStreamPermissionsReader(ABC):
    """
    This class is responsible for reading file permissions and Identities from a source.
    """

    def __init__(self) -> None:
        self._config = None

    @property
    def config(self) -> Optional[AbstractFileBasedSpec]:
        return self._config

    @config.setter
    @abstractmethod
    def config(self, value: AbstractFileBasedSpec) -> None:
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamPermissionsReader's's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        ...

    @abstractmethod
    def get_file_acl_permissions(self, file: RemoteFile, logger: logging.Logger) -> Dict[str, Any]:
        """
        This function should return the allow list for a given file, i.e. the list of all identities and their permission levels associated with it

        e.g.
        def get_file_acl_permissions(self, file: RemoteFile, logger: logging.Logger):
            api_conn = some_api.conn(credentials=SOME_CREDENTIALS)
            result = api_conn.get_file_permissions_info(file.id)
            return MyPermissionsModel(
                id=result["id"],
                access_control_list = result["access_control_list"],
                is_public = result["is_public"],
                ).dict()
        """
        ...

    @abstractmethod
    def load_identity_groups(self, logger: logging.Logger) -> Iterable[Dict[str, Any]]:
        """
        This function should return the Identities in a determined "space" or "domain" where the file metadata (ACLs) are fetched and ACLs items (Identities) exists.

        e.g.
        def load_identity_groups(self, logger: logging.Logger) -> Iterable[Dict[str, Any]]:
            api_conn = some_api.conn(credentials=SOME_CREDENTIALS)
            users_api = api_conn.users()
            groups_api = api_conn.groups()
            members_api = self.google_directory_service.members()
            for user in users_api.list():
                yield my_identity_model(id=user.id, name=user.name, email_address=user.email, type="user").dict()
            for group in groups_api.list():
                group_obj = my_identity_model(id=group.id, name=groups.name, email_address=user.email, type="group").dict()
                for member in members_api.list(group=group):
                    group_obj.member_email_addresses = group_obj.member_email_addresses or []
                    group_obj.member_email_addresses.append(member.email)
                yield group_obj.dict()
        """
        ...

    @property
    @abstractmethod
    def file_permissions_schema(self) -> Dict[str, Any]:
        """
        This function should return the permissions schema for file permissions stream.

        e.g.
        def file_permissions_schema(self) -> Dict[str, Any]:
            # you can also follow the pattern we have for python connectors and have a json file and read from there e.g. schemas/identities.json
            return {
                  "type": "object",
                  "properties": {
                    "id": { "type": "string" },
                    "file_path": { "type": "string" },
                    "access_control_list": {
                      "type": "array",
                      "items": { "type": "string" }
                    },
                    "publicly_accessible": { "type": "boolean" }
                  }
                }
        """
        ...

    @property
    @abstractmethod
    def identities_schema(self) -> Dict[str, Any]:
        """
        This function should return the identities schema for file identity stream.

        e.g.
        def identities_schema(self) -> Dict[str, Any]:
            # you can also follow the pattern we have for python connectors and have a json file and read from there e.g. schemas/identities.json
            return {
              "type": "object",
              "properties": {
                "id": { "type": "string" },
                "remote_id": { "type": "string" },
                "name": { "type": ["null", "string"] },
                "email_address": { "type": ["null", "string"] },
                "member_email_addresses": { "type": ["null", "array"] },
                "type": { "type": "string" },
              }
            }
        """
        ...
