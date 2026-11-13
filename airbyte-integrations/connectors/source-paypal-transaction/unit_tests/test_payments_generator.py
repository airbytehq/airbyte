# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


# Add the bin directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bin"))

import payments_generator


@patch("payments_generator.requests.post")
def test_create_payment_passes_security_context(mock_post):
    """Test that create_payment correctly uses the security_context in headers."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "PAY-123", "state": "created"}
    mock_post.return_value = mock_response

    security_context = '{"actor":{"account_number":"123"}}'
    result = payments_generator.create_payment("test_token", security_context)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs[1]["headers"]["X-PAYPAL-SECURITY-CONTEXT"] == security_context
    assert result == {"id": "PAY-123", "state": "created"}


@pytest.mark.parametrize(
    "config_data",
    [
        pytest.param(
            {"client_id": "test_id", "client_secret": "test_secret"},
            id="missing_security_context",
        ),
        pytest.param(
            {"client_id": "test_id", "client_secret": "test_secret", "security_context": ""},
            id="empty_security_context",
        ),
    ],
)
@patch("payments_generator.get_paypal_token", return_value="mock_token")
@patch("payments_generator.read_json")
def test_main_create_exits_without_valid_security_context(mock_read_json, mock_get_token, config_data):
    """Test that main() exits with error when security_context is missing or empty."""
    mock_read_json.return_value = config_data

    with patch.object(sys, "argv", ["payments_generator.py", "create"]):
        with pytest.raises(SystemExit) as exc_info:
            payments_generator.main()
        assert exc_info.value.code == 1


@patch("payments_generator.create_payment", return_value={"id": "PAY-123"})
@patch("payments_generator.get_paypal_token", return_value="mock_token")
@patch("payments_generator.read_json")
def test_main_create_with_security_context_succeeds(mock_read_json, mock_get_token, mock_create):
    """Test that main() calls create_payment when security_context is provided."""
    mock_read_json.return_value = {
        "client_id": "test_id",
        "client_secret": "test_secret",
        "security_context": '{"actor":{"account_number":"123"}}',
    }

    with patch.object(sys, "argv", ["payments_generator.py", "create"]):
        payments_generator.main()

    mock_create.assert_called_once_with("mock_token", '{"actor":{"account_number":"123"}}')
