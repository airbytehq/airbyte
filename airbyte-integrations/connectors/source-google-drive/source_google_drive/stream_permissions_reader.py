# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Iterator, List, Tuple

import pytz
from google.oauth2 import credentials, service_account
from googleapiclient.discovery import build

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.file_based_stream_permissions_reader import AbstractFileBasedStreamPermissionsReader
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from source_google_drive.exceptions import ErrorFetchingMetadata
from source_google_drive.spec import RemoteIdentity, RemoteIdentityType, RemotePermissions, SourceGoogleDriveSpec


DRIVE_SERVICE_SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.member.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
]

PUBLIC_PERMISSION_IDS = [
    "anyoneWithLink",
    "anyoneCanFind",
    "domainCanFind",
    "domainWithLink",
]


def datetime_now() -> datetime:
    return datetime.now(pytz.UTC)


class SourceGoogleDriveStreamPermissionsReader(AbstractFileBasedStreamPermissionsReader):
    def __init__(self):
        super().__init__()
        self._drive_service = None
        self._directory_service = None

    @property
    def config(self) -> SourceGoogleDriveSpec:
        return self._config

    @config.setter
    def config(self, value: SourceGoogleDriveSpec):
        assert isinstance(value, SourceGoogleDriveSpec)
        self._config = value

    def _build_google_service(self, service_name: str, version: str, scopes: List[str] = None):
        if self.config is None:
            # We shouldn't hit this; config should always get set before attempting to
            # list or read files.
            raise ValueError(f"Source config is missing; cannot create the Google {service_name} client.")
        try:
            if self.config.credentials.auth_type == "Client":
                creds = credentials.Credentials.from_authorized_user_info(self.config.credentials.dict())
            else:
                creds = service_account.Credentials.from_service_account_info(
                    json.loads(self.config.credentials.service_account_info), scopes=scopes
                )
            google_service = build(service_name, version, credentials=creds)
        except Exception as e:
            raise AirbyteTracedException(
                internal_message=str(e),
                message=f"Could not authenticate with Google {service_name}. Please check your credentials.",
                failure_type=FailureType.config_error,
                exception=e,
            )

        return google_service

    @property
    def google_drive_service(self):
        if self._drive_service is None:
            self._drive_service = self._build_google_service("drive", "v3")
        return self._drive_service

    @property
    def google_directory_service(self):
        if self._directory_service is None:
            self._directory_service = self._build_google_service("admin", "directory_v1", DRIVE_SERVICE_SCOPES)
        return self._directory_service

    def _get_looping_google_api_list_response(
        self, service: Any, key: str, args: dict[str, Any], logger: logging.Logger
    ) -> Iterator[dict[str, Any]]:
        try:
            looping = True
            next_page_token: str | None = None
            while looping:
                rsp = service.list(pageToken=next_page_token, **args).execute()
                next_page_token = rsp.get("nextPageToken")
                items: list[dict[str, Any]] = rsp.get(key)

                if items is None or len(items) == 0:
                    looping = False
                    break

                if rsp.get("nextPageToken") is None:
                    looping = False
                else:
                    next_page_token = rsp.get("nextPageToken")

                for item in items:
                    yield item
        except Exception as e:
            logger.error(f"There was an error listing {key} with {args}: {str(e)}")
            raise e

    def _to_remote_file_identity(self, identity: dict[str, Any]) -> RemoteIdentity | None:
        if identity.get("id") in PUBLIC_PERMISSION_IDS:
            return None
        if identity.get("deleted") is True:
            return None

        return RemoteIdentity(
            modified_at=datetime.now(),
            id=uuid.uuid4(),
            remote_id=identity.get("emailAddress"),
            name=identity.get("name"),
            email_address=identity.get("emailAddress"),
            type=identity.get("type"),
            description=None,
        )

    def get_file_permissions(self, file_id: str, file_name: str, logger: logging.Logger) -> Tuple[List[RemoteIdentity], bool]:
        """
        Retrieves the permissions of a file in Google Drive and checks for public access.

        Args:
            file_id (str): The file to get permissions for.
            file_name (str): The name of the file to get permissions for.
            logger (logging.Logger): Logger for debugging and information.

        Returns:
            Tuple(List[RemoteFileIdentity], boolean): A list of RemoteFileIdentity objects containing permission details.
        """
        try:
            request = self.google_drive_service.permissions().list(
                fileId=file_id,
                fields="permissions, permissions/role, permissions/type, permissions/id, permissions/emailAddress",
                supportsAllDrives=True,
            )
            response = request.execute()
            permissions = response.get("permissions", [])
            is_public = False

            remote_identities = []

            for p in permissions:
                identity = self._to_remote_file_identity(p)
                if p.get("id") in PUBLIC_PERMISSION_IDS:
                    is_public = True
                if identity is not None:
                    remote_identities.append(identity)

            return remote_identities, is_public
        except Exception as e:
            raise ErrorFetchingMetadata(f"An error occurred while retrieving file permissions: {str(e)}")

    def get_file_acl_permissions(self, file: Any, logger: logging.Logger) -> Dict[str, Any]:
        remote_identities, is_public = self.get_file_permissions(file.id, file_name=file.uri, logger=logger)
        return RemotePermissions(
            id=file.id,
            file_path=file.uri,
            allowed_identity_remote_ids=[p.remote_id for p in remote_identities],
            publicly_accessible=is_public,
        ).dict(exclude_none=True)

    def load_identity_groups(self, logger: logging.Logger) -> Iterator[Dict[str, Any]]:
        domain = self.config.delivery_method.domain
        if not domain:
            logger.info("No domain provided. Trying to fetch identities from the user workspace.")
            api_args = {"customer": "my_customer"}
        else:
            api_args = {"domain": domain}

        users_api = self.google_directory_service.users()
        groups_api = self.google_directory_service.groups()
        members_api = self.google_directory_service.members()

        for user in self._get_looping_google_api_list_response(users_api, "users", args=api_args, logger=logger):
            rfp = RemoteIdentity(
                id=uuid.uuid4(),
                remote_id=user["primaryEmail"],
                name=user["name"]["fullName"] if user["name"] is not None else None,
                email_address=user["primaryEmail"],
                member_email_addresses=[x["address"] for x in user["emails"]],
                type=RemoteIdentityType.USER,
                modified_at=datetime_now(),
            )
            yield rfp.dict()

        for group in self._get_looping_google_api_list_response(groups_api, "groups", args=api_args, logger=logger):
            rfp = RemoteIdentity(
                id=uuid.uuid4(),
                remote_id=group["email"],
                name=group["name"],
                email_address=group["email"],
                type=RemoteIdentityType.GROUP,
                modified_at=datetime_now(),
            )

            for member in self._get_looping_google_api_list_response(members_api, "members", {"groupKey": group["id"]}, logger):
                rfp.member_email_addresses = rfp.member_email_addresses or []
                rfp.member_email_addresses.append(member["email"])

            yield rfp.dict()

    @property
    def file_permissions_schema(self) -> Dict[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("file_permissions")

    @property
    def identities_schema(self) -> Dict[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("identities")
