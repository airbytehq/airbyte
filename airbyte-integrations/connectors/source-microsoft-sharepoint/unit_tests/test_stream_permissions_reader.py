# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
import requests
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
