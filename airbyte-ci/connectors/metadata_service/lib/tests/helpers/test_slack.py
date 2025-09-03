#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

import pytest

from metadata_service.helpers.slack import send_slack_message


@pytest.mark.parametrize(
    "slack_token,should_send,description",
    [
        ("xoxb-test-token", True, "token present - should send"),
        (None, False, "no token - should not send"),
    ],
)
def test_send_slack_message_environment_conditions(monkeypatch, slack_token, should_send, description):
    """Test send_slack_message behavior with different SLACK_TOKEN configurations."""
    if slack_token:
        monkeypatch.setenv("SLACK_TOKEN", slack_token)
    else:
        monkeypatch.delenv("SLACK_TOKEN", raising=False)

    with patch("metadata_service.helpers.slack.WebClient") as mock_webclient_class:
        mock_webclient = Mock()
        mock_webclient.chat_postMessage = Mock()
        mock_webclient_class.return_value = mock_webclient

        channel = "#test-channel"
        message = "Test message"

        success, error_msg = send_slack_message(channel, message)

        if should_send:
            mock_webclient_class.assert_called_once_with(token=slack_token)
            expected_message = message + "\n"
            mock_webclient.chat_postMessage.assert_called_once_with(channel=channel, text=expected_message)
            assert success is True
            assert error_msg is None
        else:
            mock_webclient_class.assert_not_called()
            mock_webclient.chat_postMessage.assert_not_called()
            assert success is True  # No error when token not present - expected behavior
            assert error_msg is None


@pytest.mark.parametrize(
    "exception_location,exception_type,description",
    [
        ("webclient_constructor", Exception, "WebClient constructor raises generic exception"),
        ("webclient_constructor", ConnectionError, "WebClient constructor raises connection error"),
        ("chat_post_message", Exception, "chat_postMessage raises generic exception"),
        ("chat_post_message", ConnectionError, "chat_postMessage raises connection error"),
    ],
)
def test_send_slack_message_error_handling(monkeypatch, exception_location, exception_type, description):
    """Test send_slack_message gracefully handles various error scenarios without crashing."""
    monkeypatch.setenv("SLACK_TOKEN", "xoxb-test-token")

    channel = "#test-channel"
    message = "Test message"

    if exception_location == "webclient_constructor":
        with patch("metadata_service.helpers.slack.WebClient", side_effect=exception_type("Mocked error")):
            success, error_msg = send_slack_message(channel, message)

            assert success is False
            assert "Mocked error" in error_msg
            assert isinstance(error_msg, str)

    elif exception_location == "chat_post_message":
        with patch("metadata_service.helpers.slack.WebClient") as mock_webclient_class:
            mock_webclient = Mock()
            mock_webclient.chat_postMessage = Mock(side_effect=exception_type("Mocked error"))
            mock_webclient_class.return_value = mock_webclient

            success, error_msg = send_slack_message(channel, message)

            mock_webclient_class.assert_called_once_with(token="xoxb-test-token")
            mock_webclient.chat_postMessage.assert_called_once()

            assert success is False
            assert "Mocked error" in error_msg
            assert isinstance(error_msg, str)
