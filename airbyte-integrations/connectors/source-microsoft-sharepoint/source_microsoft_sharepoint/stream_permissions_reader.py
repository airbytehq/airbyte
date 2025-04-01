# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple

import requests
from office365.directory.groups.collection import GroupCollection
from office365.directory.users.collection import UserCollection
from office365.graph_client import GraphClient
from office365.runtime.auth.token_response import TokenResponse
from office365.sharepoint.client_context import ClientContext

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.file_based_stream_permissions_reader import AbstractFileBasedStreamPermissionsReader
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from source_microsoft_sharepoint.exceptions import ErrorFetchingMetadata
from source_microsoft_sharepoint.spec import RemoteIdentity, RemoteIdentityType, RemotePermissions, SourceMicrosoftSharePointSpec
from source_microsoft_sharepoint.stream_reader import MicrosoftSharePointRemoteFile, SourceMicrosoftSharePointClient
from source_microsoft_sharepoint.utils import execute_query_with_retry, execute_request_direct_with_retry


class SourceMicrosoftSharePointStreamPermissionsReader(AbstractFileBasedStreamPermissionsReader):
    def __init__(self):
        super().__init__()
        self._auth_client = None
        self._one_drive_client = None
        self._config = None

    @property
    def config(self) -> SourceMicrosoftSharePointSpec:
        return self._config

    @config.setter
    def config(self, value: SourceMicrosoftSharePointSpec):
        """
        The FileBasedSource reads and parses configuration from a file, then sets this configuration in its StreamReader. While it only
        uses keys from its abstract configuration, concrete StreamReader implementations may need additional keys for third-party
        authentication. Therefore, subclasses of AbstractFileBasedStreamReader should verify that the value in their config setter
        matches the expected config type for their StreamReader.
        """
        assert isinstance(value, SourceMicrosoftSharePointSpec)
        self._config = value

    @property
    def auth_client(self):
        # Lazy initialization of the auth_client
        if self._auth_client is None:
            self._auth_client = SourceMicrosoftSharePointClient(self._config)
        return self._auth_client

    def _get_headers(self) -> Dict[str, str]:
        access_token = self.auth_client._get_access_token()["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    @property
    def one_drive_client(self):
        # Lazy initialization of the one_drive_client
        if self._one_drive_client is None:
            self._one_drive_client = self.auth_client.client
        return self._one_drive_client

    def get_token_response_object(self, tenant_prefix: str = None) -> Callable:
        """ "
        When building a ClientContext using with_access_token method,
        the token_func param is expected to be a method/callable that returns a TokenResponse object.

        tenant_prefix is used to determine the scope of the access token.
        return: A callable that returns a TokenResponse object.
        """
        return self.auth_client.get_token_response_object_wrapper(tenant_prefix=tenant_prefix)

    @lru_cache(maxsize=None)
    def get_site(self, graph_client: GraphClient, site_url: str = None):
        if site_url:
            site = execute_query_with_retry(graph_client.sites.get_by_url(site_url))
        else:
            site = execute_query_with_retry(graph_client.sites.root.get())
        return site

    @staticmethod
    def get_site_prefix(site):
        site_url = site.web_url
        host_name = site.site_collection.hostname
        return site_url, host_name.split(".")[0]

    def get_client_context(self):
        site_url, root_site_prefix = self.get_site_prefix(self.get_site(self.one_drive_client))
        client_context = ClientContext(site_url).with_access_token(self.get_token_response_object(tenant_prefix=root_site_prefix))
        return client_context

    def get_users(self) -> UserCollection:
        users = execute_query_with_retry(self.one_drive_client.users.get())
        return users

    def get_users_identities(self) -> Iterator[Dict[str, Any]]:
        users = self.get_users()
        if users:
            for user in users:
                rfp = RemoteIdentity(
                    remote_id=user.id,
                    display_name=user.properties["displayName"],
                    user_principal_name=user.user_principal_name,
                    email_address=user.mail,
                    type=RemoteIdentityType.USER,
                    modified_at=datetime.now(),
                    description=None,
                )
                yield rfp.dict()

    def get_groups(self) -> GroupCollection:
        groups = execute_query_with_retry(self.one_drive_client.groups.get())
        return groups

    def get_groups_identities(self) -> Iterator[Dict[str, Any]]:
        groups = self.get_groups()
        if groups:
            for group in groups:
                # Get members of the group
                member_info = self.get_group_members(group.id)

                rfp = RemoteIdentity(
                    remote_id=group.id,
                    display_name=group.display_name,
                    description=group.properties["description"],
                    email_address=group.mail,
                    type=RemoteIdentityType.GROUP,
                    modified_at=datetime.now(),
                    members=member_info,
                )
                yield rfp.dict()

    def get_group_members(self, group_id: str) -> List[Dict[str, str]]:
        """
        Retrieves the members of a specific group using the Microsoft Graph API.

        Args:
            group_id (str): The ID of the group to get members for.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing member ID and type.
        """
        try:
            headers = self._get_headers()
            url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            members = response.json().get("value", [])

            # Extract member IDs and types
            member_info = []
            for member in members:
                if member.get("id"):
                    # Extract the type from @odata.type which is in format "#microsoft.graph.user", "#microsoft.graph.group", etc.
                    odata_type = member.get("@odata.type", "")
                    member_type = odata_type.split(".")[-1] if "." in odata_type else None
                    if not member_type:
                        raise ValueError(f"Unrecognized member type for member ID {member.get('id')} in group {group_id}.")
                    # Try to get the identity type directly from RemoteIdentityType enum
                    try:
                        identity_type = RemoteIdentityType(member_type).value
                        member_info.append({"remote_id": member.get("id"), "type": identity_type})
                    except ValueError:
                        # Log the error and skip this member
                        logging.warning(
                            f"Unrecognized member type '{member_type}' for member ID {member.get('id')} in group {group_id}. Skipping this member."
                        )
                        continue

            return member_info
        except Exception as e:
            logging.warning(f"Failed to retrieve members for group {group_id}: {str(e)}")
            return []

    def get_site_users(self) -> UserCollection:
        client_context = self.get_client_context()
        site_users = client_context.web.site_users
        client_context.load(site_users)
        execute_query_with_retry(client_context)
        return site_users

    def get_site_users_identities(self) -> Iterator[Dict[str, Any]]:
        site_users = self.get_site_users()
        if site_users:
            for site_user in site_users:
                rfp = RemoteIdentity(
                    remote_id=site_user.id,
                    title=site_user.properties["Title"],
                    login_name=site_user.login_name,
                    user_principal_name=site_user.user_principal_name,
                    email_address=site_user.properties["Email"],
                    type=RemoteIdentityType.SITE_USER,
                    modified_at=datetime.now(),
                )
                yield rfp.dict()

    def get_site_groups(self) -> GroupCollection:
        client_context = self.get_client_context()
        site_groups = client_context.web.site_groups
        client_context.load(site_groups)
        execute_query_with_retry(client_context)
        return site_groups

    def get_site_groups_identities(self) -> Iterator[Dict[str, Any]]:
        site_groups = self.get_site_groups()
        if site_groups:
            for site_group in site_groups:
                # Get members of the site group
                member_info = self.get_site_group_members(site_group)

                rfp = RemoteIdentity(
                    remote_id=site_group.id,
                    title=site_group.properties["Title"],
                    description=site_group.properties["Description"],
                    type=RemoteIdentityType.SITE_GROUP,
                    modified_at=datetime.now(),
                    members=member_info,
                )
                yield rfp.dict()

    def _get_site_group_members_client_context(self, group_id: str) -> List[Dict[str, str]]:
        """
        Use Office365 client context to get site group members.

        Args:
            group_id (str): The ID of the site group.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing member ID and type.

        Raises:
            Exception: If the client context operations fail.
        """
        client_context = self.get_client_context()

        # Try to get the group by ID
        group = client_context.web.site_groups.get_by_id(group_id)
        users = group.users

        # Load the users with a specific query to avoid permission issues
        client_context.load(users, ["Id", "Title", "Email"])

        # Execute the query with retry
        execute_query_with_retry(client_context)

        # Process the users
        member_info = []
        for user in users:
            if hasattr(user, "id") and user.id:
                # For site groups, members are typically site users
                member_info.append({"remote_id": user.id, "type": RemoteIdentityType.SITE_USER.value})

        return member_info

    def get_site_group_members(self, site_group) -> List[Dict[str, str]]:
        """
        Retrieves the members of a specific SharePoint site group using the client context.

        Args:
            site_group: The site group object to get members for.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing member ID and type.
        """
        try:
            group_id = site_group.id
            logging.info(f"Getting members for site group {group_id} using client context...")
            return self._get_site_group_members_client_context(group_id)
        except Exception as e:
            logging.warning(f"Failed to retrieve members for site group {site_group.id}: {str(e)}")
            return []

    def get_applications(self):
        applications = execute_query_with_retry(self.one_drive_client.applications.get())
        return applications

    def get_applications_identities(self) -> Iterator[Dict[str, Any]]:
        applications = self.get_applications()
        if applications:
            for application in applications:
                rfp = RemoteIdentity(
                    remote_id=application.id,
                    display_name=application.display_name,
                    description=application.properties["description"],
                    type=RemoteIdentityType.APPLICATION,
                    modified_at=datetime.now(),
                )
                yield rfp.dict()

    def get_devices(self):
        devices = execute_request_direct_with_retry(self.one_drive_client, "devices")
        return devices.json().get("value")

    def get_devices_identities(self) -> Iterator[Dict[str, Any]]:
        devices = self.get_devices()
        if devices:
            for device in devices:
                rfp = RemoteIdentity(
                    remote_id=device.get("id"),
                    display_name=device.get("displayName"),
                    type=RemoteIdentityType.DEVICE,
                    modified_at=datetime.now(),
                )
                yield rfp.dict()

    def get_file_permissions(self, file: MicrosoftSharePointRemoteFile, logger: logging.Logger) -> Tuple[List[RemoteIdentity], bool]:
        """
        Retrieves the permissions of a file in Microsoft SharePoint and checks for public access.

        Args:
            file (MicrosoftSharePointRemoteFile): The file to get permissions for.
            logger (logging.Logger): Logger for debugging and information.

        Returns:
            Tuple(List[RemoteFileIdentity], boolean): A list of RemoteFileIdentity objects containing permission details.
        """
        try:
            headers = self._get_headers()
            url = f"https://graph.microsoft.com/v1.0/drives/{file.drive_id}/items/{file.id}/permissions"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            permissions = response.json().get("value", [])
            is_public = False

            remote_identities = []

            for p in permissions:
                identities = self._to_remote_file_identities(p)
                # todo: I am not sure if this is correct, need to revisit docs for sharing links:
                # https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0#sharing-links
                if (
                    p.get("link")
                    and p["link"].get("scope") == "anonymous"
                    and not p.get("grantedToIdentitiesV2")
                    and not p.get("grantedToIdentities")
                ):
                    is_public = True
                if identities is not None:
                    remote_identities.extend(identities)
            return remote_identities, is_public
        except Exception as e:
            raise ErrorFetchingMetadata(f"An error occurred while retrieving file permissions: {str(e)}")

    def _to_remote_file_identities(self, permissions: dict[str, Any]) -> Iterable[RemoteIdentity] | None:
        """
        Converts a permission object to a list of RemoteIdentity objects.

        From documentation:
        grantedToIdentitiesV2: For link type permissions, the details of the users to whom permission was granted. Read-only.
        grantedToV2: For user type permissions, the details of the users and applications for this permission. Read-only.
        ref: https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0
        """
        identities = []

        def unroll_permission_identity(permission_identity_item: dict[str, Any]):
            for identity_type in permission_identity_item:
                user_info = permission_identity_item[identity_type]
                remote_identity_type = RemoteIdentityType(identity_type)
                identities.append(
                    RemoteIdentity(
                        modified_at=datetime.now(),
                        remote_id=user_info.get("id"),
                        display_name=user_info.get("displayName"),
                        email_address=user_info.get("email"),
                        login_name=user_info.get("loginName"),
                        type=remote_identity_type,
                        description=None,
                    )
                )

        permission_identities_collection = permissions.get("grantedToIdentitiesV2", [])
        for permission_identity in permission_identities_collection:
            unroll_permission_identity(permission_identity)
        permission_identity = permissions.get("grantedToV2", {})
        unroll_permission_identity(permission_identity)
        return identities

    def get_file_acl_permissions(self, file: MicrosoftSharePointRemoteFile, logger: logging.Logger) -> Dict[str, Any]:
        remote_identities, is_public = self.get_file_permissions(file, logger=logger)
        return RemotePermissions(
            id=file.id,
            file_path=file.uri,
            allowed_identity_remote_ids=[{"identity_type": p.type, "id": p.remote_id} for p in remote_identities],
            publicly_accessible=is_public,
        ).dict(exclude_none=True)

    @property
    def file_permissions_schema(self) -> Dict[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("file_permissions")

    @property
    def identities_schema(self) -> Dict[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("identities")

    def load_identity_groups(self, logger: logging.Logger) -> Iterator[Dict[str, Any]]:
        yield from self.get_users_identities()
        yield from self.get_groups_identities()
        yield from self.get_site_users_identities()
        yield from self.get_site_groups_identities()
        yield from self.get_applications_identities()
        yield from self.get_devices_identities()
