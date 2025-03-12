# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
import requests
from office365.directory.groups.collection import GroupCollection
from office365.directory.users.collection import UserCollection
from source_microsoft_sharepoint.exceptions import ErrorFetchingMetadata
from source_microsoft_sharepoint.spec import RemoteIdentity, RemoteIdentityType, SourceMicrosoftSharePointSpec
from source_microsoft_sharepoint.stream_permissions_reader import SourceMicrosoftSharePointStreamPermissionsReader
from source_microsoft_sharepoint.stream_reader import MicrosoftSharePointRemoteFile


@pytest.fixture
def setup_permissions_reader_class():
    reader = SourceMicrosoftSharePointStreamPermissionsReader()  # Instantiate your class here
    config = Mock(spec=SourceMicrosoftSharePointSpec)
    config.credentials = Mock()
    config.credentials.auth_type = "Client"
    reader.config = config  # Set up the necessary configuration

    # Mock the client creation
    with patch("source_microsoft_sharepoint.stream_permissions_reader.SourceMicrosoftSharePointClient") as mock_client_class:
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
                    name="Test User",
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
                    name="Test User 1",
                    email_address="test1@example.com",
                    login_name="testuser1",
                    type=RemoteIdentityType.USER,
                    description=None,
                ),
                RemoteIdentity(
                    modified_at=datetime.now(),
                    remote_id="group1",
                    name="Test Group",
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
def test_get_file_permissions(setup_permissions_reader_class, permissions_response, expected_identities, expected_is_public):
    """Test get_file_permissions method with different permission scenarios."""
    instance = setup_permissions_reader_class
    mock_file = MicrosoftSharePointRemoteFile(
        uri="test.txt",
        download_url="https://example.com/test.txt",
        last_modified=datetime.now(),
        id="test_id",
        drive_id="test_drive_id",
        from_shared_drive=False,
    )
    mock_logger = Mock(spec=logging.Logger)

    # Mock the API response
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = permissions_response
        mock_get.return_value = mock_response

        # Mock the headers
        with patch.object(instance, "_get_headers", return_value={"Authorization": "Bearer test_token"}):
            identities, is_public = instance.get_file_permissions(mock_file, mock_logger)

            # Verify the API call
            mock_get.assert_called_once_with(
                f"https://graph.microsoft.com/v1.0/drives/{mock_file.drive_id}/items/{mock_file.id}/permissions",
                headers={"Authorization": "Bearer test_token"},
            )

            # Compare the results
            # Since modified_at is dynamic, we'll compare other fields
            assert len(identities) == len(expected_identities)
            for actual, expected in zip(identities, expected_identities):
                assert actual.remote_id == expected.remote_id
                assert actual.name == expected.name
                assert actual.email_address == expected.email_address
                assert actual.login_name == expected.login_name
                assert actual.type == expected.type
                assert actual.description == expected.description

            assert is_public == expected_is_public


def test_get_file_permissions_error(setup_permissions_reader_class):
    """Test get_file_permissions method when an error occurs."""
    instance = setup_permissions_reader_class
    mock_file = MicrosoftSharePointRemoteFile(
        uri="test.txt",
        download_url="https://example.com/test.txt",
        last_modified=datetime.now(),
        id="test_id",
        drive_id="test_drive_id",
        from_shared_drive=False,
    )
    mock_logger = Mock(spec=logging.Logger)

    # Mock the API response to raise an exception
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Mock the headers
        with patch.object(instance, "_get_headers", return_value={"Authorization": "Bearer test_token"}):
            with pytest.raises(ErrorFetchingMetadata) as exc_info:
                instance.get_file_permissions(mock_file, mock_logger)

            assert (
                str(exc_info.value)
                == "An error occurred while retrieving file permissions: Test error Contact Support if you need assistance.\n"
            )


def test_load_identity_groups_users(setup_permissions_reader_class):
    """Test load_identity_groups method for users."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock user data
    mock_user = Mock()
    mock_user.id = "user1"
    mock_user.properties = {
        "displayName": "Test User",
        "userPrincipalName": "test.user@example.com",
    }
    mock_user.user_principal_name = "test.user@example.com"
    mock_user.mail = "test.user@example.com"

    # Mock all methods except get_users
    with (
        patch.object(instance, "get_groups", return_value=[]),
        patch.object(instance, "get_site_users", return_value=[]),
        patch.object(instance, "get_site_groups", return_value=[]),
        patch.object(instance, "get_applications", return_value=[]),
        patch.object(instance, "get_devices", return_value=[]),
        patch.object(instance, "get_users", return_value=[mock_user]),  # This is the method we're testing
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "user1"
        assert identity["name"] == "Test User"
        assert identity["description"] == "test.user@example.com"
        assert identity["email_address"] == "test.user@example.com"
        assert identity["type"] == RemoteIdentityType.USER


def test_load_identity_groups_groups(setup_permissions_reader_class):
    """Test load_identity_groups method for groups."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock group data
    mock_group = Mock()
    mock_group.id = "group1"
    mock_group.display_name = "Test Group"
    mock_group.properties = {
        "description": "Test Group Description",
    }
    mock_group.mail = "group@example.com"

    # Mock all methods except get_groups
    with (
        patch.object(instance, "get_users", return_value=[]),
        patch.object(instance, "get_site_users", return_value=[]),
        patch.object(instance, "get_site_groups", return_value=[]),
        patch.object(instance, "get_applications", return_value=[]),
        patch.object(instance, "get_devices", return_value=[]),
        patch.object(instance, "get_groups", return_value=[mock_group]),  # This is the method we're testing
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "group1"
        assert identity["name"] == "Test Group"
        assert identity["description"] == "Test Group Description"
        assert identity["email_address"] == "group@example.com"
        assert identity["type"] == RemoteIdentityType.GROUP


def test_load_identity_groups_site_users(setup_permissions_reader_class):
    """Test load_identity_groups method for site users."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock site user data
    mock_site_user = Mock()
    mock_site_user.id = "site_user1"
    mock_site_user.properties = {
        "Title": "Test Site User",
        "Email": "site.user@example.com",
    }
    mock_site_user.user_principal_name = "site.user@example.com"

    # Mock client context
    mock_client_context = Mock()
    mock_client_context.web.site_users = [mock_site_user]
    mock_client_context.load = Mock()
    mock_client_context.execute_query = Mock()

    # Mock all methods except get_site_users
    with (
        patch.object(instance, "get_users", return_value=[]),
        patch.object(instance, "get_groups", return_value=[]),
        patch.object(instance, "get_site_groups", return_value=[]),
        patch.object(instance, "get_applications", return_value=[]),
        patch.object(instance, "get_devices", return_value=[]),
        patch.object(instance, "get_client_context", return_value=mock_client_context),  # Required for get_site_users to work
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "site_user1"
        assert identity["name"] == "Test Site User"
        assert identity["description"] == "site.user@example.com"
        assert identity["email_address"] == "site.user@example.com"
        assert identity["type"] == RemoteIdentityType.SITE_USER


def test_load_identity_groups_site_groups(setup_permissions_reader_class):
    """Test load_identity_groups method for site groups."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock site group data
    mock_site_group = Mock()
    mock_site_group.id = "site_group1"
    mock_site_group.properties = {
        "Title": "Test Site Group",
        "Description": "Test Site Group Description",
    }

    # Mock client context
    mock_client_context = Mock()
    mock_client_context.web.site_groups = [mock_site_group]
    mock_client_context.load = Mock()
    mock_client_context.execute_query = Mock()

    # Mock all methods except get_site_groups
    with (
        patch.object(instance, "get_users", return_value=[]),
        patch.object(instance, "get_groups", return_value=[]),
        patch.object(instance, "get_site_users", return_value=[]),
        patch.object(instance, "get_applications", return_value=[]),
        patch.object(instance, "get_devices", return_value=[]),
        patch.object(instance, "get_client_context", return_value=mock_client_context),  # Required for get_site_groups to work
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "site_group1"
        assert identity["name"] == "Test Site Group"
        assert identity["description"] == "Test Site Group Description"
        assert identity["type"] == RemoteIdentityType.SITE_GROUP


def test_load_identity_groups_applications(setup_permissions_reader_class):
    """Test load_identity_groups method for applications."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock application data
    mock_application = Mock()
    mock_application.id = "app1"
    mock_application.display_name = "Test Application"
    mock_application.properties = {
        "description": "Test Application Description",
    }

    # Mock all methods except get_applications
    with (
        patch.object(instance, "get_users", return_value=[]),
        patch.object(instance, "get_groups", return_value=[]),
        patch.object(instance, "get_site_users", return_value=[]),
        patch.object(instance, "get_site_groups", return_value=[]),
        patch.object(instance, "get_devices", return_value=[]),
        patch.object(instance, "get_applications", return_value=[mock_application]),  # This is the method we're testing
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "app1"
        assert identity["name"] == "Test Application"
        assert identity["description"] == "Test Application Description"
        assert identity["type"] == RemoteIdentityType.APPLICATION


def test_load_identity_groups_devices(setup_permissions_reader_class):
    """Test load_identity_groups method for devices."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock device data
    mock_device_response = {
        "value": [
            {
                "id": "device1",
                "displayName": "Test Device",
            }
        ]
    }

    # Mock all methods except get_devices
    with (
        patch.object(instance, "get_users", return_value=[]),
        patch.object(instance, "get_groups", return_value=[]),
        patch.object(instance, "get_site_users", return_value=[]),
        patch.object(instance, "get_site_groups", return_value=[]),
        patch.object(instance, "get_applications", return_value=[]),
        patch.object(instance, "get_devices", return_value=mock_device_response["value"]),  # This is the method we're testing
    ):
        # Get the identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got the expected identity
        assert len(identities) == 1
        identity = identities[0]
        assert identity["remote_id"] == "device1"
        assert identity["name"] == "Test Device"
        assert identity["type"] == RemoteIdentityType.DEVICE


def test_load_identity_groups_all_types(setup_permissions_reader_class):
    """Test load_identity_groups method with all types of identities present."""
    instance = setup_permissions_reader_class
    mock_logger = Mock(spec=logging.Logger)

    # Mock user data
    mock_user = Mock()
    mock_user.id = "user1"
    mock_user.properties = {"displayName": "Test User", "userPrincipalName": "test.user@example.com"}
    mock_user.user_principal_name = "test.user@example.com"
    mock_user.mail = "test.user@example.com"

    # Mock group data
    mock_group = Mock()
    mock_group.id = "group1"
    mock_group.display_name = "Test Group"
    mock_group.properties = {"description": "Test Group Description"}
    mock_group.mail = "group@example.com"

    # Mock site user data
    mock_site_user = Mock()
    mock_site_user.id = "site_user1"
    mock_site_user.properties = {"Title": "Test Site User", "Email": "site.user@example.com"}
    mock_site_user.user_principal_name = "site.user@example.com"

    # Mock site group data
    mock_site_group = Mock()
    mock_site_group.id = "site_group1"
    mock_site_group.properties = {"Title": "Test Site Group", "Description": "Test Site Group Description"}

    # Mock application data
    mock_application = Mock()
    mock_application.id = "app1"
    mock_application.display_name = "Test Application"
    mock_application.properties = {"description": "Test Application Description"}

    # Mock device data
    mock_device_response = {"value": [{"id": "device1", "displayName": "Test Device"}]}

    # Mock client context for site users and groups
    mock_client_context = Mock()
    mock_client_context.web.site_users = [mock_site_user]
    mock_client_context.web.site_groups = [mock_site_group]
    mock_client_context.load = Mock()
    mock_client_context.execute_query = Mock()

    # Mock all methods to return their respective data
    with (
        patch.object(instance, "get_users", return_value=[mock_user]),
        patch.object(instance, "get_groups", return_value=[mock_group]),
        patch.object(instance, "get_applications", return_value=[mock_application]),
        patch.object(instance, "get_devices", return_value=mock_device_response["value"]),
        patch.object(instance, "get_client_context", return_value=mock_client_context),
    ):
        # Get all identities
        identities = list(instance.load_identity_groups(mock_logger))

        # Verify we got all expected identities
        assert len(identities) == 6  # One of each type
        identity_types = [identity["type"] for identity in identities]
        assert RemoteIdentityType.USER in identity_types
        assert RemoteIdentityType.GROUP in identity_types
        assert RemoteIdentityType.SITE_USER in identity_types
        assert RemoteIdentityType.SITE_GROUP in identity_types
        assert RemoteIdentityType.APPLICATION in identity_types
        assert RemoteIdentityType.DEVICE in identity_types


def test_get_group_members_success(setup_permissions_reader_class):
    """Test get_group_members method with successful API response."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"

    # Mock API response with different member types
    mock_response = {
        "value": [
            {"id": "user1", "@odata.type": "#microsoft.graph.user", "displayName": "Test User"},
            {"id": "group1", "@odata.type": "#microsoft.graph.group", "displayName": "Test Group"},
            {"id": "app1", "@odata.type": "#microsoft.graph.application", "displayName": "Test App"},
            {"id": "device1", "@odata.type": "#microsoft.graph.device", "displayName": "Test Device"},
        ]
    }

    # Mock the requests.get method
    with patch("requests.get") as mock_get:
        mock_response_obj = Mock()
        mock_response_obj.raise_for_status = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_get.return_value = mock_response_obj

        # Mock the _get_headers method
        with patch.object(instance, "_get_headers", return_value={"Authorization": "Bearer test_token"}):
            # Call the method
            result = instance.get_group_members(group_id)

            # Verify the API call
            mock_get.assert_called_once_with(
                f"https://graph.microsoft.com/v1.0/groups/{group_id}/members", headers={"Authorization": "Bearer test_token"}
            )

            # Verify the result
            assert len(result) == 4
            assert result[0] == {"remote_id": "user1", "type": "user"}
            assert result[1] == {"remote_id": "group1", "type": "group"}
            assert result[2] == {"remote_id": "app1", "type": "application"}
            assert result[3] == {"remote_id": "device1", "type": "device"}


def test_get_group_members_unrecognized_type(setup_permissions_reader_class):
    """Test get_group_members method with an unrecognized member type."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"

    # Mock API response with an unrecognized member type
    mock_response = {
        "value": [
            {"id": "user1", "@odata.type": "#microsoft.graph.user", "displayName": "Test User"},
            {"id": "unknown1", "@odata.type": "#microsoft.graph.unknownType", "displayName": "Unknown Type"},
        ]
    }

    # Mock the requests.get method
    with patch("requests.get") as mock_get:
        mock_response_obj = Mock()
        mock_response_obj.raise_for_status = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_get.return_value = mock_response_obj

        # Mock the _get_headers method
        with patch.object(instance, "_get_headers", return_value={"Authorization": "Bearer test_token"}):
            # Mock the logging
            with patch("logging.warning") as mock_warning:
                # Call the method
                result = instance.get_group_members(group_id)

                # Verify the API call
                mock_get.assert_called_once_with(
                    f"https://graph.microsoft.com/v1.0/groups/{group_id}/members", headers={"Authorization": "Bearer test_token"}
                )

                # Verify the result
                assert len(result) == 1
                assert result[0] == {"remote_id": "user1", "type": "user"}

                # Verify the warning was logged
                mock_warning.assert_called_once_with(
                    f"Unrecognized member type 'unknownType' for member ID unknown1 in group {group_id}. Skipping this member."
                )


def test_get_group_members_api_error(setup_permissions_reader_class):
    """Test get_group_members method when the API call fails."""
    instance = setup_permissions_reader_class
    group_id = "test_group_id"

    # Mock the requests.get method to raise an exception
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        # Mock the _get_headers method
        with patch.object(instance, "_get_headers", return_value={"Authorization": "Bearer test_token"}):
            # Mock the logging
            with patch("logging.warning") as mock_warning:
                # Call the method
                result = instance.get_group_members(group_id)

                # Verify the result is an empty list
                assert result == []

                # Verify the warning was logged
                mock_warning.assert_called_once_with(f"Failed to retrieve members for group {group_id}: API Error")


def test_get_site_group_members_success(setup_permissions_reader_class):
    """Test get_site_group_members method with successful client context execution."""
    instance = setup_permissions_reader_class

    # Create a mock site group
    mock_site_group = Mock()
    mock_site_group.id = "test_site_group_id"

    # Create mock users
    mock_user1 = Mock()
    mock_user1.id = "site_user1"
    mock_user1.properties = {"Title": "Site User 1", "Email": "user1@example.com"}

    mock_user2 = Mock()
    mock_user2.id = "site_user2"
    mock_user2.properties = {"Title": "Site User 2", "Email": "user2@example.com"}

    # Mock the client context and its methods
    mock_client_context = Mock()
    mock_group = Mock()
    mock_users = [mock_user1, mock_user2]

    mock_client_context.web.site_groups.get_by_id.return_value = mock_group
    mock_group.users = mock_users

    # Mock the get_client_context method
    with patch.object(instance, "get_client_context", return_value=mock_client_context):
        # Mock the execute_query_with_retry function
        with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
            # Mock the logging
            with patch("logging.info") as mock_info:
                # Call the method
                result = instance.get_site_group_members(mock_site_group)

                # Verify the client context calls
                mock_client_context.web.site_groups.get_by_id.assert_called_once_with(mock_site_group.id)
                mock_client_context.load.assert_called_once_with(mock_users, ["Id", "Title", "Email"])
                mock_execute.assert_called_once_with(mock_client_context)

                # Verify the result
                assert len(result) == 2
                assert result[0] == {"remote_id": "site_user1", "type": "siteUser"}
                assert result[1] == {"remote_id": "site_user2", "type": "siteUser"}

                # Verify the info was logged
                mock_info.assert_called_once_with(f"Getting members for site group {mock_site_group.id} using client context...")


def test_get_site_group_members_error(setup_permissions_reader_class):
    """Test get_site_group_members method when an error occurs."""
    instance = setup_permissions_reader_class

    # Create a mock site group
    mock_site_group = Mock()
    mock_site_group.id = "test_site_group_id"

    # Mock the get_client_context method to raise an exception
    with patch.object(instance, "get_client_context", side_effect=Exception("Client context error")):
        # Mock the logging
        with patch("logging.info") as mock_info:
            with patch("logging.warning") as mock_warning:
                # Call the method
                result = instance.get_site_group_members(mock_site_group)

                # Verify the result is an empty list
                assert result == []

                # Verify the logs
                mock_info.assert_called_once_with(f"Getting members for site group {mock_site_group.id} using client context...")
                mock_warning.assert_called_once_with(
                    f"Failed to retrieve members for site group {mock_site_group.id}: Client context error"
                )


def test_get_site_group_members_client_context_implementation(setup_permissions_reader_class):
    """Test the _get_site_group_members_client_context method directly."""
    instance = setup_permissions_reader_class
    group_id = "test_site_group_id"

    # Create mock users
    mock_user1 = Mock()
    type(mock_user1).id = PropertyMock(return_value="site_user1")

    mock_user2 = Mock()
    type(mock_user2).id = PropertyMock(return_value="site_user2")

    # User without an ID
    mock_user3 = Mock()
    type(mock_user3).id = PropertyMock(return_value=None)

    # Mock the client context and its methods
    mock_client_context = Mock()
    mock_group = Mock()
    mock_users = [mock_user1, mock_user2, mock_user3]

    mock_client_context.web.site_groups.get_by_id.return_value = mock_group
    mock_group.users = mock_users

    # Mock the get_client_context method
    with patch.object(instance, "get_client_context", return_value=mock_client_context):
        # Mock the execute_query_with_retry function
        with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
            # Call the method
            result = instance._get_site_group_members_client_context(group_id)

            # Verify the client context calls
            mock_client_context.web.site_groups.get_by_id.assert_called_once_with(group_id)
            mock_client_context.load.assert_called_once_with(mock_users, ["Id", "Title", "Email"])
            mock_execute.assert_called_once_with(mock_client_context)

            # Verify the result - should only include users with IDs
            assert len(result) == 2
            assert result[0] == {"remote_id": "site_user1", "type": "siteUser"}
            assert result[1] == {"remote_id": "site_user2", "type": "siteUser"}


def test_get_site_prefix(setup_permissions_reader_class):
    """Test get_site_prefix static method."""
    # Create a mock site object
    mock_site = Mock()
    mock_site.web_url = "https://airbyte.sharepoint.com/sites/TestSite"
    mock_site.site_collection.hostname = "airbyte.sharepoint.com"

    # Call the static method
    site_url, root_site_prefix = setup_permissions_reader_class.get_site_prefix(mock_site)

    # Verify the results
    assert site_url == "https://airbyte.sharepoint.com/sites/TestSite"
    assert root_site_prefix == "airbyte"


def test_get_site(setup_permissions_reader_class):
    """Test get_site method with and without site_url parameter."""
    instance = setup_permissions_reader_class
    mock_graph_client = Mock()

    # Mock for get_by_url
    mock_site_by_url = Mock()
    mock_graph_client.sites.get_by_url.return_value = mock_site_by_url

    # Mock for root.get
    mock_root_site = Mock()
    mock_graph_client.sites.root.get.return_value = mock_root_site

    # Mock execute_query_with_retry
    with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        # Set up mock_execute to return the appropriate site based on the input
        mock_execute.side_effect = lambda x: x

        # Test with site_url
        site_url = "https://airbyte.sharepoint.com/sites/TestSite"
        result_with_url = instance.get_site(mock_graph_client, site_url)

        # Verify calls
        mock_graph_client.sites.get_by_url.assert_called_once_with(site_url)
        mock_execute.assert_called_with(mock_site_by_url)
        assert result_with_url == mock_site_by_url

        # Reset mocks
        mock_execute.reset_mock()

        # Test without site_url
        result_without_url = instance.get_site(mock_graph_client)

        # Verify calls
        mock_graph_client.sites.root.get.assert_called_once()
        mock_execute.assert_called_with(mock_root_site)
        assert result_without_url == mock_root_site


def test_get_client_context(setup_permissions_reader_class):
    """Test get_client_context method."""
    instance = setup_permissions_reader_class

    # Mock get_site
    mock_site = Mock()
    mock_site.web_url = "https://airbyte.sharepoint.com/sites/TestSite"
    mock_site.site_collection.hostname = "airbyte.sharepoint.com"

    # Mock get_site_prefix to return the site URL and prefix
    site_url = "https://airbyte.sharepoint.com/sites/TestSite"
    root_site_prefix = "airbyte"

    # Mock ClientContext
    mock_client_context = Mock()
    mock_client_context_with_token = Mock()
    mock_client_context.with_access_token.return_value = mock_client_context_with_token

    # Mock auth_client and its get_token_response_object_wrapper method
    mock_auth_client = Mock()
    mock_token_func = Mock()
    mock_auth_client.get_token_response_object_wrapper.return_value = mock_token_func

    # Set the mock auth_client directly to the _auth_client attribute
    instance._auth_client = mock_auth_client

    # Set the mock one_drive_client directly to the _one_drive_client attribute
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client

    with (
        patch.object(instance, "get_site", return_value=mock_site) as mock_get_site,
        patch.object(instance, "get_site_prefix", return_value=(site_url, root_site_prefix)) as mock_get_site_prefix,
        patch(
            "source_microsoft_sharepoint.stream_permissions_reader.ClientContext", return_value=mock_client_context
        ) as mock_client_context_class,
    ):
        # Call the method
        result = instance.get_client_context()

        # Verify calls
        mock_get_site.assert_called_once_with(mock_one_drive_client)
        mock_get_site_prefix.assert_called_once_with(mock_site)
        mock_client_context_class.assert_called_once_with(site_url)
        mock_auth_client.get_token_response_object_wrapper.assert_called_once_with(tenant_prefix=root_site_prefix)
        mock_client_context.with_access_token.assert_called_once_with(mock_token_func)

        # Verify result
        assert result == mock_client_context_with_token


def test_get_token_response_object(setup_permissions_reader_class):
    """Test get_token_response_object method."""
    instance = setup_permissions_reader_class

    # Mock auth_client and its get_token_response_object_wrapper method
    mock_auth_client = Mock()
    mock_token_func = Mock()
    mock_auth_client.get_token_response_object_wrapper.return_value = mock_token_func

    # Set the mock auth_client directly to the _auth_client attribute
    instance._auth_client = mock_auth_client

    # Test with tenant_prefix
    result_with_prefix = instance.get_token_response_object(tenant_prefix="airbyte")
    mock_auth_client.get_token_response_object_wrapper.assert_called_once_with(tenant_prefix="airbyte")
    assert result_with_prefix == mock_token_func

    # Reset mock
    mock_auth_client.get_token_response_object_wrapper.reset_mock()

    # Test without tenant_prefix
    result_without_prefix = instance.get_token_response_object()
    mock_auth_client.get_token_response_object_wrapper.assert_called_once_with(tenant_prefix=None)
    assert result_without_prefix == mock_token_func


def test_get_users(setup_permissions_reader_class):
    """Test get_users method."""
    instance = setup_permissions_reader_class

    # Mock users collection
    mock_users = Mock(spec=UserCollection)

    # Mock one_drive_client by setting the _one_drive_client attribute directly
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.users.get.return_value = mock_users

    # Mock execute_query_with_retry
    with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        # Set up mock_execute to return the users collection
        mock_execute.return_value = mock_users

        # Call the method
        result = instance.get_users()

        # Verify calls
        mock_one_drive_client.users.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_users)

        # Verify result
        assert result == mock_users


def test_get_groups(setup_permissions_reader_class):
    """Test get_groups method."""
    instance = setup_permissions_reader_class

    # Mock groups collection
    mock_groups = Mock(spec=GroupCollection)

    # Mock one_drive_client by setting the _one_drive_client attribute directly
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.groups.get.return_value = mock_groups

    # Mock execute_query_with_retry
    with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        # Set up mock_execute to return the groups collection
        mock_execute.return_value = mock_groups

        # Call the method
        result = instance.get_groups()

        # Verify calls
        mock_one_drive_client.groups.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_groups)

        # Verify result
        assert result == mock_groups


def test_get_site_users(setup_permissions_reader_class):
    """Test get_site_users method."""
    instance = setup_permissions_reader_class

    # Mock site users collection
    mock_site_users = Mock(spec=UserCollection)

    # Mock client context
    mock_client_context = Mock()
    mock_client_context.web.site_users = mock_site_users

    # Mock get_client_context
    with patch.object(instance, "get_client_context", return_value=mock_client_context) as mock_get_client_context:
        # Call the method
        result = instance.get_site_users()

        # Verify calls
        mock_get_client_context.assert_called_once()
        mock_client_context.load.assert_called_once_with(mock_site_users)
        mock_client_context.execute_query.assert_called_once()

        # Verify result
        assert result == mock_site_users


def test_get_site_groups(setup_permissions_reader_class):
    """Test get_site_groups method."""
    instance = setup_permissions_reader_class

    # Mock site groups collection
    mock_site_groups = Mock(spec=GroupCollection)

    # Mock client context
    mock_client_context = Mock()
    mock_client_context.web.site_groups = mock_site_groups

    # Mock get_client_context
    with patch.object(instance, "get_client_context", return_value=mock_client_context) as mock_get_client_context:
        # Call the method
        result = instance.get_site_groups()

        # Verify calls
        mock_get_client_context.assert_called_once()
        mock_client_context.load.assert_called_once_with(mock_site_groups)
        mock_client_context.execute_query.assert_called_once()

        # Verify result
        assert result == mock_site_groups


def test_get_applications(setup_permissions_reader_class):
    """Test get_applications method."""
    instance = setup_permissions_reader_class

    # Mock applications collection
    mock_applications = Mock()

    # Mock one_drive_client by setting the _one_drive_client attribute directly
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.applications.get.return_value = mock_applications

    # Mock execute_query_with_retry
    with patch("source_microsoft_sharepoint.stream_permissions_reader.execute_query_with_retry") as mock_execute:
        # Set up mock_execute to return the applications collection
        mock_execute.return_value = mock_applications

        # Call the method
        result = instance.get_applications()

        # Verify calls
        mock_one_drive_client.applications.get.assert_called_once()
        mock_execute.assert_called_once_with(mock_applications)

        # Verify result
        assert result == mock_applications


def test_get_devices(setup_permissions_reader_class):
    """Test get_devices method."""
    instance = setup_permissions_reader_class

    # Mock devices response
    mock_devices_response = Mock()
    mock_devices_response.json.return_value = {"value": [{"id": "device1"}, {"id": "device2"}]}

    # Mock one_drive_client by setting the _one_drive_client attribute directly
    mock_one_drive_client = Mock()
    instance._one_drive_client = mock_one_drive_client
    mock_one_drive_client.execute_request_direct.return_value = mock_devices_response

    # Call the method
    result = instance.get_devices()

    # Verify calls
    mock_one_drive_client.execute_request_direct.assert_called_once_with("devices")
    mock_devices_response.raise_for_status.assert_called_once()

    # Verify result
    assert result == [{"id": "device1"}, {"id": "device2"}]
