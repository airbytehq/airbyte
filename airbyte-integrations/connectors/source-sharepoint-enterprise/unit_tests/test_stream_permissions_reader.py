# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
import requests
from office365.directory.groups.collection import GroupCollection
from office365.directory.users.collection import UserCollection
from source_sharepoint_enterprise.exceptions import ErrorFetchingMetadata
from source_sharepoint_enterprise.spec import (
    RemoteIdentity,
    RemoteIdentityType,
    SourceMicrosoftSharePointSpec,
)
from source_sharepoint_enterprise.stream_permissions_reader import (
    SourceMicrosoftSharePointStreamPermissionsReader,
)
from source_sharepoint_enterprise.stream_reader import MicrosoftSharePointRemoteFile


@pytest.fixture
def setup_permissions_reader_class():
    reader = SourceMicrosoftSharePointStreamPermissionsReader()  # Instantiate your class here
    config = Mock(spec=SourceMicrosoftSharePointSpec)
    config.credentials = Mock()
    config.credentials.auth_type = "Client"
    reader.config = config  # Set up the necessary configuration

    # Mock the client creation
    with patch("source_sharepoint_enterprise.sharepoint_client.SourceMicrosoftSharePointClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.client = Mock()  # Mock the client attribute of SourceMicrosoftSharePointClient
        yield reader


@pytest.mark.parametrize(
    "permissions_response, expected_identities, expected_is_public",
    [
        # Test case 1: Empty permissions
        ({"value": []}, [], False),
        # Test case 2: Public link permission
        (
            {
                "value": [
                    {
                        "link": {"scope": "anonymous"},
                        "grantedToIdentitiesV2": [],
                        "grantedToIdentities": [],
                    }
                ]
            },
            [],
            True,
        ),
        # Test case 3: User permissions
        (
            {
                "value": [
                    {
                        "grantedToV2": {
                            "user": {
                                "id": "user1",
                                "displayName": "Test User",
                                "email": "test@example.com",
                                "loginName": "testuser",
                            }
                        }
                    }
                ]
            },
            [
                RemoteIdentity(
                    modified_at=datetime.now(),
                    remote_id="user1",
                    display_name="Test User",
                    email_address="test@example.com",
                    login_name="testuser",
                    type=RemoteIdentityType.USER,
                    description=None,
                )
            ],
            False,
        ),
        # Test case 4: Multiple identities
        (
            {
                "value": [
                    {
                        "grantedToIdentitiesV2": [
                            {
                                "user": {
                                    "id": "user1",
                                    "displayName": "Test User 1",
                                    "email": "test1@example.com",
                                    "loginName": "testuser1",
                                }
                            }
                        ],
                        "grantedToV2": {
                            "group": {
                                "id": "group1",
                                "displayName": "Test Group",
                                "email": "group@example.com",
                                "loginName": "testgroup",
                            }
                        },
                    }
                ]
            },
            [
                RemoteIdentity(
                    modified_at=datetime.now(),
                    remote_id="user1",
                    display_name="Test User 1",
                    email_address="test1@example.com",
                    login_name="testuser1",
                    type=RemoteIdentityType.USER,
                    description=None,
                ),
                RemoteIdentity(
                    modified_at=datetime.now(),
                    remote_id="group1",
                    display_name="Test Group",
                    email_address="group@example.com",
                    login_name="testgroup",
                    type=RemoteIdentityType.GROUP,
                    description=None,
                ),
            ],
            False,
        ),
    ],
)
def test_get_file_permissions(
    setup_permissions_reader_class,
    permissions_response,
    expected_identities,
    expected_is_public,
):
    """Test get_file_permissions method with different permission scenarios.
    Tests empty permissions, public links, user permissions, and multiple identity types."""

    instance = setup_permissions_reader_class
    mock_file = MicrosoftSharePointRemoteFile(
        uri="test.txt",
        download_url="https://example.com/test.txt",
        last_modified=datetime.now(),
        created_at=datetime.now(),
        id="test_id",
        drive_id="test_drive_id",
        from_shared_drive=False,
    )
    mock_logger = Mock(spec=logging.Logger)
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = permissions_response

    with (
        patch("requests.get", return_value=mock_response) as mock_get,
        patch.object(
            instance,
            "_get_headers",
            return_value={"Authorization": "Bearer test_token"},
        ) as mock_headers,
    ):
        identities, is_public = instance.get_file_permissions(mock_file, mock_logger)

        mock_get.assert_called_once_with(
            f"https://graph.microsoft.com/v1.0/drives/{mock_file.drive_id}/items/{mock_file.id}/permissions",
            headers={"Authorization": "Bearer test_token"},
        )

        assert len(identities) == len(expected_identities)
        for actual, expected in zip(identities, expected_identities):
            assert actual.remote_id == expected.remote_id
            assert actual.display_name == expected.display_name
            assert actual.email_address == expected.email_address
            assert actual.login_name == expected.login_name
            assert actual.type == expected.type
            assert actual.description == expected.description

        assert is_public == expected_is_public


def test_get_file_permissions_error(setup_permissions_reader_class):
    """Tests error handling in get_file_permissions method.
    Verifies correct exception is raised with proper error message when API request fails."""

    instance = setup_permissions_reader_class
    test_uri = "test.txt"
    test_url = "https://example.com/test.txt"
    test_id = "test_id"
    test_drive_id = "test_drive_id"
    error_message = "Test error"
    auth_token = "Bearer test_token"

    mock_file = MicrosoftSharePointRemoteFile(
        uri=test_uri,
        download_url=test_url,
        last_modified=datetime.now(),
        created_at=datetime.now(),
        id=test_id,
        drive_id=test_drive_id,
        from_shared_drive=False,
    )
    mock_logger = Mock(spec=logging.Logger)

    with (
        patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException(error_message),
        ) as mock_get,
        patch.object(instance, "_get_headers", return_value={"Authorization": auth_token}) as mock_headers,
    ):
        with pytest.raises(ErrorFetchingMetadata) as exc_info:
            instance.get_file_permissions(mock_file, mock_logger)

        expected_error = f"An error occurred while retrieving file permissions: {error_message} Contact Support if you need assistance.\n"
        assert str(exc_info.value) == expected_error


def test_load_identity_groups_users(setup_permissions_reader_class):
    """Tests load_identity_groups correctly handles user identities.
    Verifies method correctly returns user identities from get_users_identities."""

    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    user_id = "user1"
    user_name = "Test User"
    user_email = "test.user@example.com"

    mock_user_identity = {
        "remote_id": user_id,
        "display_name": user_name,
        "user_principal_name": user_email,
        "email_address": user_email,
        "type": RemoteIdentityType.USER,
    }

    with (
        patch.object(instance, "get_groups_identities", return_value=[]),
        patch.object(instance, "get_site_users_identities", return_value=[]),
        patch.object(instance, "get_site_groups_identities", return_value=[]),
        patch.object(instance, "get_applications_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[]),
        patch.object(instance, "get_users_identities", return_value=[mock_user_identity]),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        identity = identities[0]
        assert identity == mock_user_identity


def test_load_identity_groups_groups(setup_permissions_reader_class):
    """Tests load_identity_groups correctly handles group identities.
    Verifies method correctly returns group identities from get_groups_identities."""

    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    group_id = "group1"
    group_name = "Test Group"
    group_description = "Test Group Description"
    group_email = "group@example.com"

    mock_group_identity = {
        "remote_id": group_id,
        "display_name": group_name,
        "description": group_description,
        "email_address": group_email,
        "type": RemoteIdentityType.GROUP,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[]),
        patch.object(instance, "get_site_users_identities", return_value=[]),
        patch.object(instance, "get_site_groups_identities", return_value=[]),
        patch.object(instance, "get_applications_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[]),
        patch.object(instance, "get_groups_identities", return_value=[mock_group_identity]),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        identity = identities[0]
        assert identity == mock_group_identity


def test_load_identity_groups_site_users(setup_permissions_reader_class):
    """Tests load_identity_groups correctly handles site user identities.
    Verifies method correctly returns site user identities from get_site_users_identities."""

    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    site_user_id = "site_user1"
    site_user_title = "Test Site User"
    user_email = "site.user@example.com"

    mock_site_user_identity = {
        "remote_id": site_user_id,
        "title": site_user_title,
        "user_principal_name": user_email,
        "email_address": user_email,
        "login_name": user_email,
        "type": RemoteIdentityType.SITE_USER,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[]),
        patch.object(instance, "get_groups_identities", return_value=[]),
        patch.object(instance, "get_site_groups_identities", return_value=[]),
        patch.object(instance, "get_applications_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[]),
        patch.object(
            instance,
            "get_site_users_identities",
            return_value=[mock_site_user_identity],
        ),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        identity = identities[0]
        assert identity == mock_site_user_identity


def test_load_identity_groups_site_groups(setup_permissions_reader_class):
    """Tests that load_identity_groups correctly processes and returns site group identities.
    Mocks all dependency methods and verifies correct identity processing."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    mock_site_group_identity = {
        "remote_id": "site_group1",
        "title": "Test Site Group",
        "description": "Test Site Group Description",
        "type": RemoteIdentityType.SITE_GROUP,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[]),
        patch.object(instance, "get_groups_identities", return_value=[]),
        patch.object(instance, "get_site_users_identities", return_value=[]),
        patch.object(instance, "get_applications_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[]),
        patch.object(
            instance,
            "get_site_groups_identities",
            return_value=[mock_site_group_identity],
        ),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        assert identities[0] == mock_site_group_identity


def test_load_identity_groups_applications(setup_permissions_reader_class):
    """Tests that load_identity_groups correctly processes and returns application identities.
    Mocks all dependency methods and verifies correct identity processing."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    mock_application_identity = {
        "remote_id": "app1",
        "display_name": "Test Application",
        "description": "Test Application Description",
        "type": RemoteIdentityType.APPLICATION,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[]),
        patch.object(instance, "get_groups_identities", return_value=[]),
        patch.object(instance, "get_site_users_identities", return_value=[]),
        patch.object(instance, "get_site_groups_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[]),
        patch.object(
            instance,
            "get_applications_identities",
            return_value=[mock_application_identity],
        ),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        assert identities[0] == mock_application_identity


def test_load_identity_groups_devices(setup_permissions_reader_class):
    """Tests that load_identity_groups correctly processes and returns device identities.
    Mocks all dependency methods and verifies correct identity processing."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    mock_device_identity = {
        "remote_id": "device1",
        "display_name": "Test Device",
        "type": RemoteIdentityType.DEVICE,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[]),
        patch.object(instance, "get_groups_identities", return_value=[]),
        patch.object(instance, "get_site_users_identities", return_value=[]),
        patch.object(instance, "get_site_groups_identities", return_value=[]),
        patch.object(instance, "get_applications_identities", return_value=[]),
        patch.object(instance, "get_devices_identities", return_value=[mock_device_identity]),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 1
        assert identities[0] == mock_device_identity


def test_load_identity_groups_all_types(setup_permissions_reader_class):
    """Tests load_identity_groups processes and returns all identity types.
    Verifies that each identity type is correctly retrieved from the corresponding method."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    mock_user_identity = {
        "remote_id": "user1",
        "display_name": "Test User",
        "type": RemoteIdentityType.USER,
    }
    mock_group_identity = {
        "remote_id": "group1",
        "display_name": "Test Group",
        "type": RemoteIdentityType.GROUP,
    }
    mock_site_user_identity = {
        "remote_id": "site_user1",
        "title": "Test Site User",
        "type": RemoteIdentityType.SITE_USER,
    }
    mock_site_group_identity = {
        "remote_id": "site_group1",
        "title": "Test Site Group",
        "type": RemoteIdentityType.SITE_GROUP,
    }
    mock_application_identity = {
        "remote_id": "app1",
        "display_name": "Test Application",
        "type": RemoteIdentityType.APPLICATION,
    }
    mock_device_identity = {
        "remote_id": "device1",
        "display_name": "Test Device",
        "type": RemoteIdentityType.DEVICE,
    }

    with (
        patch.object(instance, "get_users_identities", return_value=[mock_user_identity]),
        patch.object(instance, "get_groups_identities", return_value=[mock_group_identity]),
        patch.object(
            instance,
            "get_site_users_identities",
            return_value=[mock_site_user_identity],
        ),
        patch.object(
            instance,
            "get_site_groups_identities",
            return_value=[mock_site_group_identity],
        ),
        patch.object(
            instance,
            "get_applications_identities",
            return_value=[mock_application_identity],
        ),
        patch.object(instance, "get_devices_identities", return_value=[mock_device_identity]),
    ):
        identities = list(instance.load_identity_groups(mock_logger))

        assert len(identities) == 6
        identity_types = [identity["type"] for identity in identities]
        assert RemoteIdentityType.USER in identity_types
        assert RemoteIdentityType.GROUP in identity_types
        assert RemoteIdentityType.SITE_USER in identity_types
        assert RemoteIdentityType.SITE_GROUP in identity_types
        assert RemoteIdentityType.APPLICATION in identity_types
        assert RemoteIdentityType.DEVICE in identity_types


def test_get_users_identities(setup_permissions_reader_class):
    """Tests get_users_identities correctly formats user data from get_users.
    Verifies the proper mapping of user properties to RemoteIdentity fields."""
    instance = setup_permissions_reader_class

    mock_user = Mock()
    mock_user.id = "user1"
    mock_user.properties = {
        "displayName": "Test User",
        "userPrincipalName": "test.user@example.com",
    }
    mock_user.user_principal_name = "test.user@example.com"
    mock_user.mail = "test.user@example.com"

    with patch.object(instance, "get_users", return_value=[mock_user]):
        formatted_users = list(instance.get_users_identities())

        assert len(formatted_users) == 1
        assert formatted_users[0]["remote_id"] == "user1"
        assert formatted_users[0]["display_name"] == "Test User"
        assert formatted_users[0]["user_principal_name"] == "test.user@example.com"
        assert formatted_users[0]["email_address"] == "test.user@example.com"
        assert formatted_users[0]["type"] == RemoteIdentityType.USER


def test_get_groups_identities(setup_permissions_reader_class):
    """Tests get_groups_identities correctly formats group data from get_groups.
    Verifies proper mapping of group properties to RemoteIdentity fields with member information."""
    instance = setup_permissions_reader_class

    mock_group = Mock()
    mock_group.id = "group1"
    mock_group.display_name = "Test Group"
    mock_group.properties = {
        "description": "Test Group Description",
    }
    mock_group.mail = "group@example.com"

    mock_member_info = [{"remote_id": "member1", "type": "user"}]

    with (
        patch.object(instance, "get_groups", return_value=[mock_group]),
        patch.object(instance, "get_group_members", return_value=mock_member_info),
    ):
        formatted_groups = list(instance.get_groups_identities())

        assert len(formatted_groups) == 1
        assert formatted_groups[0]["remote_id"] == "group1"
        assert formatted_groups[0]["display_name"] == "Test Group"
        assert formatted_groups[0]["description"] == "Test Group Description"
        assert formatted_groups[0]["email_address"] == "group@example.com"
        assert formatted_groups[0]["type"] == RemoteIdentityType.GROUP
        assert formatted_groups[0]["members"] == mock_member_info


def test_get_site_users_identities(setup_permissions_reader_class):
    """Tests get_site_users_identities correctly formats site user data from get_site_users.
    Verifies proper mapping of site user properties to RemoteIdentity fields."""
    instance = setup_permissions_reader_class

    mock_site_user = Mock()
    mock_site_user.id = "site_user1"
    mock_site_user.properties = {
        "Title": "Test Site User",
        "Email": "site.user@example.com",
    }
    mock_site_user.user_principal_name = "site.user@example.com"
    mock_site_user.login_name = "site.user@example.com"

    with patch.object(instance, "get_site_users", return_value=[mock_site_user]):
        formatted_site_users = list(instance.get_site_users_identities())

        assert len(formatted_site_users) == 1
        assert formatted_site_users[0]["remote_id"] == "site_user1"
        assert formatted_site_users[0]["title"] == "Test Site User"
        assert formatted_site_users[0]["login_name"] == "site.user@example.com"
        assert formatted_site_users[0]["user_principal_name"] == "site.user@example.com"
        assert formatted_site_users[0]["email_address"] == "site.user@example.com"
        assert formatted_site_users[0]["type"] == RemoteIdentityType.SITE_USER


def test_get_site_groups_identities(setup_permissions_reader_class):
    """Tests get_site_groups_identities correctly formats site group data from get_site_groups.
    Verifies proper mapping of site group properties to RemoteIdentity fields with member information."""
    instance = setup_permissions_reader_class

    site_group_id = "site_group1"
    site_group_title = "Test Site Group"
    site_group_description = "Test Site Group Description"

    mock_site_group = Mock()
    mock_site_group.id = site_group_id
    mock_site_group.properties = {
        "Title": site_group_title,
        "Description": site_group_description,
    }

    mock_member_info = [{"remote_id": "member1", "type": "siteUser"}]

    with (
        patch.object(instance, "get_site_groups", return_value=[mock_site_group]),
        patch.object(instance, "get_site_group_members", return_value=mock_member_info),
    ):
        formatted_site_groups = list(instance.get_site_groups_identities())

        assert len(formatted_site_groups) == 1
        assert formatted_site_groups[0]["remote_id"] == site_group_id
        assert formatted_site_groups[0]["title"] == site_group_title
        assert formatted_site_groups[0]["description"] == site_group_description
        assert formatted_site_groups[0]["type"] == RemoteIdentityType.SITE_GROUP
        assert formatted_site_groups[0]["members"] == mock_member_info


def test_get_applications_identities(setup_permissions_reader_class):
    """Tests get_applications_identities correctly formats application data from get_applications.
    Verifies proper mapping of application properties to RemoteIdentity fields."""
    instance = setup_permissions_reader_class

    app_id = "app1"
    app_name = "Test Application"
    app_description = "Test Application Description"

    mock_application = Mock()
    mock_application.id = app_id
    mock_application.display_name = app_name
    mock_application.properties = {
        "description": app_description,
    }

    with patch.object(instance, "get_applications", return_value=[mock_application]):
        formatted_applications = list(instance.get_applications_identities())

        assert len(formatted_applications) == 1
        assert formatted_applications[0]["remote_id"] == app_id
        assert formatted_applications[0]["display_name"] == app_name
        assert formatted_applications[0]["description"] == app_description
        assert formatted_applications[0]["type"] == RemoteIdentityType.APPLICATION


def test_get_devices(setup_permissions_reader_class):
    """Tests get_devices correctly retrieves and processes device data.
    Verifies API call is made properly and results are returned as expected."""
    instance = setup_permissions_reader_class
    device_data = [{"id": "device1"}, {"id": "device2"}]

    mock_devices_response = Mock()
    mock_devices_response.json.return_value = {"value": device_data}

    mock_one_drive_client = Mock()

    with (
        patch.object(
            SourceMicrosoftSharePointStreamPermissionsReader,
            "one_drive_client",
            new_callable=PropertyMock,
            return_value=mock_one_drive_client,
        ),
        patch(
            "source_sharepoint_enterprise.stream_permissions_reader.execute_request_direct_with_retry",
            return_value=mock_devices_response,
        ) as mock_execute_with_retry,
    ):
        result = instance.get_devices()

        mock_execute_with_retry.assert_called_once_with(mock_one_drive_client, "devices")
        assert result == device_data


def test_get_group_members_success(setup_permissions_reader_class):
    """Tests get_group_members successfully processes API response with different member types.
    Verifies correct extraction of member IDs and types from Graph API response."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"
    auth_token = "Bearer test_token"

    mock_response = {
        "value": [
            {
                "id": "user1",
                "@odata.type": "#microsoft.graph.user",
                "displayName": "Test User",
            },
            {
                "id": "group1",
                "@odata.type": "#microsoft.graph.group",
                "displayName": "Test Group",
            },
            {
                "id": "app1",
                "@odata.type": "#microsoft.graph.application",
                "displayName": "Test App",
            },
            {
                "id": "device1",
                "@odata.type": "#microsoft.graph.device",
                "displayName": "Test Device",
            },
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.raise_for_status = Mock()
    mock_response_obj.json.return_value = mock_response

    with (
        patch("requests.get", return_value=mock_response_obj) as mock_get,
        patch.object(instance, "_get_headers", return_value={"Authorization": auth_token}),
    ):
        result = instance.get_group_members(group_id)

        mock_get.assert_called_once_with(
            f"https://graph.microsoft.com/v1.0/groups/{group_id}/members",
            headers={"Authorization": auth_token},
        )

        assert len(result) == 4
        assert result[0] == {"remote_id": "user1", "type": "user"}
        assert result[1] == {"remote_id": "group1", "type": "group"}
        assert result[2] == {"remote_id": "app1", "type": "application"}
        assert result[3] == {"remote_id": "device1", "type": "device"}


def test_get_group_members_unrecognized_type(setup_permissions_reader_class):
    """Tests get_group_members properly handles unrecognized member types.
    Verifies warning is logged and only recognized member types are returned."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"
    auth_token = "Bearer test_token"

    mock_response = {
        "value": [
            {
                "id": "user1",
                "@odata.type": "#microsoft.graph.user",
                "displayName": "Test User",
            },
            {
                "id": "unknown1",
                "@odata.type": "#microsoft.graph.unknownType",
                "displayName": "Unknown Type",
            },
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.raise_for_status = Mock()
    mock_response_obj.json.return_value = mock_response

    with (
        patch("requests.get", return_value=mock_response_obj) as mock_get,
        patch.object(instance, "_get_headers", return_value={"Authorization": auth_token}),
        patch("logging.warning") as mock_warning,
    ):
        result = instance.get_group_members(group_id)

        mock_get.assert_called_once_with(
            f"https://graph.microsoft.com/v1.0/groups/{group_id}/members",
            headers={"Authorization": auth_token},
        )

        assert len(result) == 1
        assert result[0] == {"remote_id": "user1", "type": "user"}

        mock_warning.assert_called_once_with(
            f"Unrecognized member type 'unknownType' for member ID unknown1 in group {group_id}. Skipping this member."
        )


def test_get_group_members_api_error(setup_permissions_reader_class):
    """Tests get_group_members properly handles API errors.
    Verifies warning is logged and empty list is returned when API request fails."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"
    auth_token = "Bearer test_token"
    error_message = "API Error"

    with (
        patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException(error_message),
        ) as mock_get,
        patch.object(instance, "_get_headers", return_value={"Authorization": auth_token}),
        patch("logging.warning") as mock_warning,
    ):
        result = instance.get_group_members(group_id)

        assert result == []
        mock_warning.assert_called_once_with(f"Failed to retrieve members for group {group_id}: {error_message}")


def test_get_site_group_members_success(setup_permissions_reader_class):
    """Tests get_site_group_members correctly retrieves members using client context.
    Verifies proper extraction of user IDs and correct handling of client context operations."""
    instance = setup_permissions_reader_class
    group_id = "test_site_group_id"

    mock_site_group = Mock()
    mock_site_group.id = group_id

    mock_user1 = Mock()
    mock_user1.id = "site_user1"
    mock_user1.properties = {"Title": "Site User 1", "Email": "user1@example.com"}

    mock_user2 = Mock()
    mock_user2.id = "site_user2"
    mock_user2.properties = {"Title": "Site User 2", "Email": "user2@example.com"}

    mock_users = [mock_user1, mock_user2]
    mock_group = Mock()
    mock_group.users = mock_users

    mock_client_context = Mock()
    mock_client_context.web.site_groups.get_by_id.return_value = mock_group

    with (
        patch.object(instance, "_get_client_context", return_value=mock_client_context),
        patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute,
        patch("logging.info") as mock_info,
    ):
        result = instance.get_site_group_members(mock_site_group)

        mock_client_context.web.site_groups.get_by_id.assert_called_once_with(group_id)
        mock_client_context.load.assert_called_once_with(mock_users, ["Id", "Title", "Email"])
        mock_execute.assert_called_once_with(mock_client_context)
        mock_info.assert_called_once_with(f"Getting members for site group {group_id} using client context...")

        assert len(result) == 2
        assert result[0] == {"remote_id": "site_user1", "type": "siteUser"}
        assert result[1] == {"remote_id": "site_user2", "type": "siteUser"}


def test_get_site_group_members_error(setup_permissions_reader_class):
    """Tests get_site_group_members properly handles client context errors.
    Verifies warning is logged and empty list is returned when client context fails."""
    instance = setup_permissions_reader_class
    group_id = "test_site_group_id"
    error_message = "Client context error"

    mock_site_group = Mock()
    mock_site_group.id = group_id

    with (
        patch.object(instance, "_get_client_context", side_effect=Exception(error_message)),
        patch("logging.info") as mock_info,
        patch("logging.warning") as mock_warning,
    ):
        result = instance.get_site_group_members(mock_site_group)

        assert result == []
        mock_info.assert_called_once_with(f"Getting members for site group {group_id} using client context...")
        mock_warning.assert_called_once_with(f"Failed to retrieve members for site group {group_id}: {error_message}")


def test_get_site_group_members_client_context_implementation(
    setup_permissions_reader_class,
):
    """Tests _get_site_group_members_client_context correctly extracts members with valid IDs.
    Verifies users without IDs are properly filtered from the result."""
    instance = setup_permissions_reader_class
    group_id = "test_site_group_id"

    mock_user1 = Mock()
    type(mock_user1).id = PropertyMock(return_value="site_user1")

    mock_user2 = Mock()
    type(mock_user2).id = PropertyMock(return_value="site_user2")

    mock_user3 = Mock()
    type(mock_user3).id = PropertyMock(return_value=None)

    mock_users = [mock_user1, mock_user2, mock_user3]
    mock_group = Mock()
    mock_group.users = mock_users

    mock_client_context = Mock()
    mock_client_context.web.site_groups.get_by_id.return_value = mock_group

    with (
        patch.object(instance, "_get_client_context", return_value=mock_client_context),
        patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute,
    ):
        result = instance._get_site_group_members_client_context(group_id)

        mock_client_context.web.site_groups.get_by_id.assert_called_once_with(group_id)
        mock_client_context.load.assert_called_once_with(mock_users, ["Id", "Title", "Email"])
        mock_execute.assert_called_once_with(mock_client_context)

        assert len(result) == 2
        assert result[0] == {"remote_id": "site_user1", "type": "siteUser"}
        assert result[1] == {"remote_id": "site_user2", "type": "siteUser"}


def test_get_client_context(setup_permissions_reader_class):
    """Tests _get_client_context correctly initializes a client context with access token.
    Verifies proper site URL and token configuration from auth client."""
    instance = setup_permissions_reader_class
    site_url = "https://airbyte.sharepoint.com/sites/TestSite"
    root_site_prefix = "airbyte"

    mock_client_context = Mock()
    mock_client_context_with_token = Mock()
    mock_client_context.with_access_token.return_value = mock_client_context_with_token

    mock_auth_client = Mock()
    mock_token_func = Mock()
    mock_auth_client.get_token_response_object_wrapper.return_value = mock_token_func
    instance._auth_client = mock_auth_client

    with (
        patch.object(
            SourceMicrosoftSharePointStreamPermissionsReader,
            "site_url",
            new_callable=PropertyMock,
            return_value=site_url,
        ),
        patch.object(
            SourceMicrosoftSharePointStreamPermissionsReader,
            "root_site_prefix",
            new_callable=PropertyMock,
            return_value=root_site_prefix,
        ),
        patch(
            "source_sharepoint_enterprise.sharepoint_base_reader.ClientContext",
            return_value=mock_client_context,
        ) as mock_client_context_class,
    ):
        result = instance._get_client_context()

        mock_client_context_class.assert_called_once_with(site_url)
        mock_auth_client.get_token_response_object_wrapper.assert_called_once_with(tenant_prefix=root_site_prefix)
        mock_client_context.with_access_token.assert_called_once_with(token_func=mock_token_func)
        assert result == mock_client_context_with_token


def test_get_token_response_object(setup_permissions_reader_class):
    """Tests get_token_response_object correctly delegates to auth client's wrapper method.
    Verifies tenant prefix is properly passed and result is returned directly."""
    instance = setup_permissions_reader_class
    tenant_prefix = "airbyte"

    mock_auth_client = Mock()
    mock_token_func = Mock()
    mock_auth_client.get_token_response_object_wrapper.return_value = mock_token_func
    instance._auth_client = mock_auth_client

    result = instance.get_token_response_object(tenant_prefix=tenant_prefix)

    mock_auth_client.get_token_response_object_wrapper.assert_called_once_with(tenant_prefix=tenant_prefix)
    assert result == mock_token_func


def test_get_users(setup_permissions_reader_class):
    """Tests that get_users correctly retrieves users collection from one_drive_client.
    Verifies client method is called and result is returned properly."""
    instance = setup_permissions_reader_class

    mock_users = Mock(spec=UserCollection)
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.users.get.return_value = mock_users

    with patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        mock_execute.return_value = mock_users

        result = instance.get_users()

        mock_one_drive_client.users.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_users)
        assert result == mock_users


def test_get_groups(setup_permissions_reader_class):
    """Tests that get_groups correctly retrieves groups collection from one_drive_client.
    Verifies client method is called and result is returned properly."""
    instance = setup_permissions_reader_class

    mock_groups = Mock(spec=GroupCollection)
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.groups.get.return_value = mock_groups

    with patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        mock_execute.return_value = mock_groups

        result = instance.get_groups()

        mock_one_drive_client.groups.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_groups)
        assert result == mock_groups


def test_get_site_users(setup_permissions_reader_class):
    """Tests that get_site_users correctly retrieves site user collection via client context.
    Verifies context loading and execution with proper return value."""
    instance = setup_permissions_reader_class

    mock_site_users = Mock(spec=UserCollection)
    mock_client_context = Mock()
    mock_client_context.web.site_users = mock_site_users

    with (
        patch.object(instance, "_get_client_context", return_value=mock_client_context) as mock_get_client_context,
        patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute_with_retry,
    ):
        result = instance.get_site_users()

        mock_get_client_context.assert_called_once()
        mock_client_context.load.assert_called_once_with(mock_site_users)
        mock_execute_with_retry.assert_called_once_with(mock_client_context)
        assert result == mock_site_users


def test_get_site_groups(setup_permissions_reader_class):
    """Tests that get_site_groups correctly retrieves site group collection via client context.
    Verifies context loading and execution with proper return value."""
    instance = setup_permissions_reader_class

    mock_site_groups = Mock(spec=GroupCollection)
    mock_client_context = Mock()
    mock_client_context.web.site_groups = mock_site_groups

    with (
        patch.object(instance, "_get_client_context", return_value=mock_client_context) as mock_get_client_context,
        patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute_with_retry,
    ):
        result = instance.get_site_groups()

        mock_get_client_context.assert_called_once()
        mock_client_context.load.assert_called_once_with(mock_site_groups)
        mock_execute_with_retry.assert_called_once_with(mock_client_context)
        assert result == mock_site_groups


def test_get_applications(setup_permissions_reader_class):
    """Tests that get_applications correctly retrieves applications collection from one_drive_client.
    Verifies client method is called and result is returned properly."""
    instance = setup_permissions_reader_class

    mock_applications = Mock()
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.applications.get.return_value = mock_applications

    with patch("source_sharepoint_enterprise.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        mock_execute.return_value = mock_applications

        result = instance.get_applications()

        mock_one_drive_client.applications.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_applications)
        assert result == mock_applications
