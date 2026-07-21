#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import threading
import time
from unittest.mock import MagicMock, patch

import components
import pytest
import requests
from components import _RDT_REFRESH_THRESHOLD_SECONDS, AmazonSPRdtAuthenticator


@pytest.fixture(autouse=True)
def reset_authenticator_instances():
    """Reset the module-level authenticator instances before and after each test."""
    components._authenticator_instances.clear()
    yield
    components._authenticator_instances.clear()


def _make_rdt_authenticator(include_pii: bool = True) -> AmazonSPRdtAuthenticator:
    """Create an AmazonSPRdtAuthenticator instance with mocked internals for unit testing."""
    auth = object.__new__(AmazonSPRdtAuthenticator)
    auth._rdt_token = None
    auth._rdt_fetch_time = None
    auth._rdt_fallback_to_lwa = False
    auth.restricted_resource_paths = ["/orders/v0/orders", "/orders/v0/orders/*/orderItems"]
    auth.config = {
        "include_pii": include_pii,
        "endpoint": "https://sellingpartnerapi-na.amazon.com",
    }

    # Mock the _host InterpolatedString
    mock_host = MagicMock()
    mock_host.eval.return_value = "sellingpartnerapi-na.amazon.com"
    auth._host = mock_host

    return auth


def _create_response(status_code: int, json_body: dict) -> requests.Response:
    """Create a real requests.Response object with the given status code and JSON body."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(json_body).encode("utf-8")
    return response


class TestRdtAuthenticatorGetAuthHeader:
    """Tests for AmazonSPRdtAuthenticator.get_auth_header()."""

    def test_returns_rdt_token_when_include_pii_is_true(self):
        """When include_pii is True and an RDT is cached, the RDT is used in the auth header."""
        auth = _make_rdt_authenticator(include_pii=True)
        auth._rdt_token = "rdt-token-abc123"
        auth._rdt_fetch_time = time.monotonic()

        header = auth.get_auth_header()

        assert header["x-amz-access-token"] == "rdt-token-abc123"

    def test_falls_back_to_lwa_when_include_pii_is_false(self):
        """When include_pii is False, the standard LWA token is used."""
        auth = _make_rdt_authenticator(include_pii=False)

        with patch.object(auth, "get_access_token", return_value="lwa-token-xyz"):
            header = auth.get_auth_header()

        assert header["x-amz-access-token"] == "lwa-token-xyz"

    def test_falls_back_to_lwa_when_rdt_fallback_is_set(self):
        """When _rdt_fallback_to_lwa is True, the standard LWA token is used."""
        auth = _make_rdt_authenticator(include_pii=True)
        auth._rdt_fallback_to_lwa = True

        with patch.object(auth, "get_access_token", return_value="lwa-token-xyz"):
            header = auth.get_auth_header()

        assert header["x-amz-access-token"] == "lwa-token-xyz"

    def test_fetches_rdt_when_no_cached_token(self):
        """When include_pii is True and no cached RDT, _fetch_rdt_token is called."""
        auth = _make_rdt_authenticator(include_pii=True)

        with patch.object(auth, "_fetch_rdt_token", return_value="fresh-rdt-token") as mock_fetch:
            header = auth.get_auth_header()

        mock_fetch.assert_called_once()
        assert header["x-amz-access-token"] == "fresh-rdt-token"

    def test_falls_back_to_lwa_when_fetch_returns_none(self):
        """When _fetch_rdt_token returns None (e.g., 403 fallback), LWA token is used."""
        auth = _make_rdt_authenticator(include_pii=True)

        with patch.object(auth, "_fetch_rdt_token", return_value=None):
            with patch.object(auth, "get_access_token", return_value="lwa-fallback"):
                header = auth.get_auth_header()

        assert header["x-amz-access-token"] == "lwa-fallback"


class TestRdtTokenCaching:
    """Tests for RDT token caching and refresh logic."""

    def test_returns_cached_token_when_not_expired(self):
        """A cached RDT that is within the 50-minute threshold is reused."""
        auth = _make_rdt_authenticator()
        auth._rdt_token = "cached-rdt"
        auth._rdt_fetch_time = time.monotonic()  # Just fetched

        with patch.object(auth, "_fetch_rdt_token") as mock_fetch:
            result = auth._get_rdt_token()

        mock_fetch.assert_not_called()
        assert result == "cached-rdt"

    def test_refreshes_token_when_expired(self):
        """A cached RDT older than 50 minutes triggers a fresh fetch."""
        auth = _make_rdt_authenticator()
        auth._rdt_token = "old-rdt"
        auth._rdt_fetch_time = time.monotonic() - (_RDT_REFRESH_THRESHOLD_SECONDS + 1)

        with patch.object(auth, "_fetch_rdt_token", return_value="new-rdt") as mock_fetch:
            result = auth._get_rdt_token()

        mock_fetch.assert_called_once()
        assert result == "new-rdt"

    def test_fetches_token_when_no_cache(self):
        """When there is no cached token, a fresh fetch is triggered."""
        auth = _make_rdt_authenticator()

        with patch.object(auth, "_fetch_rdt_token", return_value="first-rdt") as mock_fetch:
            result = auth._get_rdt_token()

        mock_fetch.assert_called_once()
        assert result == "first-rdt"


class TestRdtTokenFetch:
    """Tests for _fetch_rdt_token() HTTP interaction."""

    def test_successful_rdt_fetch(self):
        """A successful RDT API response caches the token and returns it."""
        auth = _make_rdt_authenticator()

        mock_response = _create_response(200, {"restrictedDataToken": "new-rdt-token-123"})

        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", return_value=mock_response) as mock_post:
                result = auth._fetch_rdt_token()

        assert result == "new-rdt-token-123"
        assert auth._rdt_token == "new-rdt-token-123"
        assert auth._rdt_fetch_time is not None
        assert auth._rdt_fallback_to_lwa is False

        # Verify the correct URL and payload were sent
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://sellingpartnerapi-na.amazon.com/tokens/2021-03-01/restrictedDataToken"
        payload = call_args[1]["json"]
        assert len(payload["restrictedResources"]) == 2
        assert payload["restrictedResources"][0]["path"] == "/orders/v0/orders"
        assert payload["restrictedResources"][0]["dataElements"] == ["buyerInfo", "shippingAddress"]
        assert payload["restrictedResources"][1]["path"] == "/orders/v0/orders/*/orderItems"

    def test_403_response_falls_back_to_lwa(self):
        """A 403 response sets _rdt_fallback_to_lwa and returns None."""
        auth = _make_rdt_authenticator()

        mock_response = _create_response(403, {"errors": [{"code": "Unauthorized", "message": "Access denied"}]})

        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", return_value=mock_response):
                result = auth._fetch_rdt_token()

        assert result is None
        assert auth._rdt_fallback_to_lwa is True
        assert auth._rdt_token is None

    def test_non_403_error_raises_config_error(self):
        """A non-403 error response raises AirbyteTracedException with config_error."""
        from airbyte_cdk.models import FailureType
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        auth = _make_rdt_authenticator()

        mock_response = _create_response(400, {"errors": [{"code": "InvalidInput", "message": "Bad request format"}]})

        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", return_value=mock_response):
                with pytest.raises(AirbyteTracedException) as exc_info:
                    auth._fetch_rdt_token()

        assert exc_info.value.failure_type == FailureType.config_error
        assert "400" in str(exc_info.value.message)

    def test_500_error_raises_backoff_exception(self):
        """A 500 error response raises DefaultBackoffException for retry."""
        from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

        auth = _make_rdt_authenticator()

        mock_response = _create_response(500, {"errors": [{"code": "InternalError", "message": "Server error"}]})
        mock_response.request = requests.PreparedRequest()
        mock_response.request.url = "https://sellingpartnerapi-na.amazon.com/tokens/2021-03-01/restrictedDataToken"

        # Call the underlying function directly to bypass the backoff decorator
        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", return_value=mock_response):
                with pytest.raises(DefaultBackoffException):
                    auth._fetch_rdt_token.__wrapped__(auth)

    def test_network_error_raises_config_error(self):
        """A network-level exception raises AirbyteTracedException with config_error."""
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        auth = _make_rdt_authenticator()

        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", side_effect=requests.ConnectionError("DNS resolution failed")):
                with pytest.raises(AirbyteTracedException) as exc_info:
                    auth._fetch_rdt_token()

        assert "DNS resolution failed" in str(exc_info.value.message)

    def test_502_error_raises_backoff_exception(self):
        """A 502 error response raises DefaultBackoffException for retry."""
        from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

        auth = _make_rdt_authenticator()

        response = requests.Response()
        response.status_code = 502
        response._content = b"Bad Gateway"
        response.request = requests.PreparedRequest()
        response.request.url = "https://sellingpartnerapi-na.amazon.com/tokens/2021-03-01/restrictedDataToken"

        # Call the underlying function directly to bypass the backoff decorator
        with patch.object(auth, "get_access_token", return_value="lwa-token"):
            with patch("components.requests.post", return_value=response):
                with pytest.raises(DefaultBackoffException):
                    auth._fetch_rdt_token.__wrapped__(auth)


class TestRdtAuthenticatorRegistration:
    """Tests for authenticator instance registration."""

    def test_multiple_authenticators_are_all_registered(self):
        """Both regular and RDT authenticators should be registered in the instances list."""
        # Simulate two authenticator instances being registered
        mock_auth1 = MagicMock()
        mock_auth2 = MagicMock()
        components._authenticator_instances.append(mock_auth1)
        components._authenticator_instances.append(mock_auth2)

        assert len(components._authenticator_instances) == 2
        assert mock_auth1 in components._authenticator_instances
        assert mock_auth2 in components._authenticator_instances


class TestRdtTokenThreadSafety:
    """Tests for thread-safe RDT token refresh (double-checked locking)."""

    def test_concurrent_refresh_only_fetches_once(self):
        """When multiple threads detect an expired RDT simultaneously, only one fetch occurs."""
        auth = _make_rdt_authenticator()
        fetch_call_count = 0
        fetch_call_lock = threading.Lock()

        def mock_fetch(self_arg=None):
            nonlocal fetch_call_count
            with fetch_call_lock:
                fetch_call_count += 1
            # Simulate network latency so threads overlap
            time.sleep(0.05)
            auth._rdt_token = "new-rdt"
            auth._rdt_fetch_time = time.monotonic()
            return "new-rdt"

        results = []
        errors = []

        def get_token():
            try:
                token = auth._get_rdt_token()
                results.append(token)
            except Exception as e:
                errors.append(e)

        with patch.object(auth, "_fetch_rdt_token", side_effect=mock_fetch):
            threads = [threading.Thread(target=get_token) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(results) == 5
        assert all(token == "new-rdt" for token in results)
        assert fetch_call_count == 1, f"Expected 1 fetch call, got {fetch_call_count}"
