# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

#
#

import os
import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest
from source_file.client import URLFile


class TestProxyCertificateSupport:
    """Test proxy and certificate support for HTTPS provider"""

    def test_https_with_proxy_only(self):
        """Test HTTPS provider with proxy_url configuration"""
        provider = {"storage": "HTTPS", "proxy_url": "http://proxy.company.com:8080"}
        url_file = URLFile("https://example.com/test.csv", provider)

        with patch("smart_open.open") as mock_smart_open:
            url_file._open()

            mock_smart_open.assert_called_once()
            args, kwargs = mock_smart_open.call_args
            transport_params = kwargs.get("transport_params", {})

            assert "proxies" in transport_params
            assert transport_params["proxies"]["http"] == "http://proxy.company.com:8080"
            assert transport_params["proxies"]["https"] == "http://proxy.company.com:8080"

    def test_https_with_certificate_only(self):
        """Test HTTPS provider with ca_certificate configuration"""
        test_cert = "-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END CERTIFICATE-----"
        provider = {"storage": "HTTPS", "ca_certificate": test_cert}
        url_file = URLFile("https://example.com/test.csv", provider)

        with (
            patch("smart_open.open") as mock_smart_open,
            patch("tempfile.mkstemp") as mock_mkstemp,
            patch("os.fdopen") as mock_fdopen,
            patch("os.unlink") as mock_unlink,
        ):
            mock_mkstemp.return_value = (123, "/tmp/test_cert.pem")
            mock_file = mock_open()
            mock_fdopen.return_value.__enter__ = Mock(return_value=mock_file.return_value)
            mock_fdopen.return_value.__exit__ = Mock(return_value=None)

            url_file._open()

            mock_mkstemp.assert_called_once_with(suffix=".pem", text=True)
            mock_fdopen.assert_called_once_with(123, "w")
            mock_file.return_value.write.assert_called_once_with(test_cert)

            mock_smart_open.assert_called_once()
            args, kwargs = mock_smart_open.call_args
            transport_params = kwargs.get("transport_params", {})
            assert transport_params["verify"] == "/tmp/test_cert.pem"

    def test_https_with_proxy_and_certificate(self):
        """Test HTTPS provider with both proxy_url and ca_certificate"""
        test_cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        provider = {"storage": "HTTPS", "proxy_url": "https://secure-proxy.company.com:3128", "ca_certificate": test_cert}
        url_file = URLFile("https://example.com/test.csv", provider)

        with patch("smart_open.open") as mock_smart_open, patch("tempfile.mkstemp") as mock_mkstemp, patch("os.fdopen") as mock_fdopen:
            mock_mkstemp.return_value = (456, "/tmp/test_cert2.pem")
            mock_file = mock_open()
            mock_fdopen.return_value.__enter__ = Mock(return_value=mock_file.return_value)
            mock_fdopen.return_value.__exit__ = Mock(return_value=None)

            url_file._open()

            mock_smart_open.assert_called_once()
            args, kwargs = mock_smart_open.call_args
            transport_params = kwargs.get("transport_params", {})

            assert "proxies" in transport_params
            assert transport_params["proxies"]["https"] == "https://secure-proxy.company.com:3128"
            assert transport_params["verify"] == "/tmp/test_cert2.pem"

    def test_https_without_proxy_or_certificate(self):
        """Test HTTPS provider without proxy or certificate (regression test)"""
        provider = {"storage": "HTTPS"}
        url_file = URLFile("https://example.com/test.csv", provider)

        with patch("smart_open.open") as mock_smart_open:
            url_file._open()

            mock_smart_open.assert_called_once()
            args, kwargs = mock_smart_open.call_args
            transport_params = kwargs.get("transport_params")

            assert transport_params is None or transport_params == {}

    def test_https_with_user_agent_and_proxy(self):
        """Test HTTPS provider with user_agent and proxy_url"""
        provider = {"storage": "HTTPS", "user_agent": True, "proxy_url": "http://proxy.test.com:8080"}
        url_file = URLFile("https://example.com/test.csv", provider)

        with patch("smart_open.open") as mock_smart_open, patch.dict("os.environ", {"AIRBYTE_VERSION": "1.2.3"}):
            url_file._open()

            mock_smart_open.assert_called_once()
            args, kwargs = mock_smart_open.call_args
            transport_params = kwargs.get("transport_params", {})

            assert "headers" in transport_params
            assert transport_params["headers"]["User-Agent"] == "Airbyte/1.2.3"
            assert "proxies" in transport_params
            assert transport_params["proxies"]["http"] == "http://proxy.test.com:8080"

    def test_certificate_cleanup_on_error(self):
        """Test certificate file cleanup when smart_open raises exception"""
        test_cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        provider = {"storage": "HTTPS", "ca_certificate": test_cert}
        url_file = URLFile("https://example.com/test.csv", provider)

        with (
            patch("smart_open.open") as mock_smart_open,
            patch("tempfile.mkstemp") as mock_mkstemp,
            patch("os.fdopen") as mock_fdopen,
            patch("os.unlink") as mock_unlink,
            patch("os.path.exists") as mock_exists,
        ):
            mock_mkstemp.return_value = (789, "/tmp/test_cert3.pem")
            mock_file = mock_open()
            mock_fdopen.return_value.__enter__ = Mock(return_value=mock_file.return_value)
            mock_fdopen.return_value.__exit__ = Mock(return_value=None)
            mock_exists.return_value = True

            mock_smart_open.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                url_file._open()

            mock_unlink.assert_called_once_with("/tmp/test_cert3.pem")

    def test_certificate_file_creation_error_cleanup(self):
        """Test certificate file cleanup when file creation fails"""
        test_cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        provider = {"storage": "HTTPS", "ca_certificate": test_cert}
        url_file = URLFile("https://example.com/test.csv", provider)

        with (
            patch("tempfile.mkstemp") as mock_mkstemp,
            patch("os.fdopen") as mock_fdopen,
            patch("os.unlink") as mock_unlink,
            patch("os.path.exists") as mock_exists,
        ):
            mock_mkstemp.return_value = (999, "/tmp/test_cert4.pem")
            mock_exists.return_value = True
            mock_fdopen.side_effect = Exception("File creation failed")

            with pytest.raises(Exception, match="File creation failed"):
                url_file._open()

            mock_unlink.assert_called_once_with("/tmp/test_cert4.pem")
