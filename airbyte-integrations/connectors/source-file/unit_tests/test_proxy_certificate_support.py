# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from source_file.client import Client, URLFile

from airbyte_cdk.entrypoint import logger


class TestProxyCertificateSupport:
    """Test proxy and certificate support for HTTPS provider"""

    def test_https_with_proxy_only(self):
        """Test HTTPS provider with proxy_url configuration"""
        http_proxy_config = {"proxy_url": "http://proxy.company.com:8080"}

        with patch.dict("os.environ", {}, clear=True), patch("source_file.client.configure_custom_http_proxy") as mock_configure:
            client = Client(
                dataset_name="test", url="https://example.com/test.csv", provider={"storage": "HTTPS"}, http_proxy=http_proxy_config
            )

            mock_configure.assert_called_once_with(http_proxy_config=http_proxy_config, logger=logger)

    def test_https_with_certificate_only(self):
        """Test HTTPS provider with ca_certificate configuration"""
        test_cert = "-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END CERTIFICATE-----"
        http_proxy_config = {"proxy_ca_certificate": test_cert}

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("source_file.proxy._install_ca_certificate") as mock_install,
            patch("source_file.client.configure_custom_http_proxy") as mock_configure,
        ):
            mock_install.return_value = Path("/tmp/test_cert.pem")

            client = Client(
                dataset_name="test", url="https://example.com/test.csv", provider={"storage": "HTTPS"}, http_proxy=http_proxy_config
            )

            mock_configure.assert_called_once_with(http_proxy_config=http_proxy_config, logger=logger)

    def test_https_with_proxy_and_certificate(self):
        """Test HTTPS provider with both proxy_url and ca_certificate"""
        test_cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        http_proxy_config = {"proxy_url": "https://secure-proxy.company.com:3128", "proxy_ca_certificate": test_cert}

        with patch.dict("os.environ", {}, clear=True), patch("source_file.client.configure_custom_http_proxy") as mock_configure:
            client = Client(
                dataset_name="test", url="https://example.com/test.csv", provider={"storage": "HTTPS"}, http_proxy=http_proxy_config
            )

            mock_configure.assert_called_once_with(http_proxy_config=http_proxy_config, logger=logger)

    def test_https_without_proxy_or_certificate(self):
        """Test HTTPS provider without proxy or certificate (regression test)"""
        with patch.dict("os.environ", {}, clear=True), patch("source_file.client.configure_custom_http_proxy") as mock_configure:
            client = Client(dataset_name="test", url="https://example.com/test.csv", provider={"storage": "HTTPS"}, http_proxy=None)

            mock_configure.assert_not_called()

    def test_https_with_user_agent_and_proxy(self):
        """Test HTTPS provider with user_agent and proxy_url"""
        http_proxy_config = {"proxy_url": "http://proxy.test.com:8080"}

        with (
            patch.dict("os.environ", {"AIRBYTE_VERSION": "1.2.3"}, clear=True),
            patch("source_file.client.configure_custom_http_proxy") as mock_configure,
        ):
            client = Client(
                dataset_name="test",
                url="https://example.com/test.csv",
                provider={"storage": "HTTPS", "user_agent": True},
                http_proxy=http_proxy_config,
            )

            mock_configure.assert_called_once_with(http_proxy_config=http_proxy_config, logger=logger)

    def test_certificate_installation(self):
        """Test certificate installation creates temporary file and sets environment variables"""
        test_cert = "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"

        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, patch.dict("os.environ", {}, clear=True):
            mock_file = mock_open()
            mock_temp_file.return_value.__enter__.return_value = mock_file.return_value
            mock_file.return_value.name = "/tmp/test_cert.pem"

            from source_file.proxy import _install_ca_certificate

            result_path = _install_ca_certificate(test_cert)

            mock_file.return_value.write.assert_called_once_with(test_cert)
            mock_file.return_value.flush.assert_called_once()

            assert os.environ.get("REQUESTS_CA_BUNDLE") == "/tmp/test_cert.pem"
            assert os.environ.get("CURL_CA_BUNDLE") == "/tmp/test_cert.pem"
            assert os.environ.get("SSL_CERT_FILE") == "/tmp/test_cert.pem"

    def test_proxy_environment_variables_set(self):
        """Test that proxy configuration sets the correct environment variables"""
        http_proxy_config = {
            "proxy_url": "http://proxy.test.com:8080",
            "proxy_ca_certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
        }

        with patch.dict("os.environ", {}, clear=True), patch("source_file.proxy._install_ca_certificate") as mock_install:
            mock_install.return_value = Path("/tmp/test_cert.pem")

            from source_file.proxy import configure_custom_http_proxy

            configure_custom_http_proxy(http_proxy_config=http_proxy_config, logger=logger)

            assert os.environ.get("HTTP_PROXY") == "http://proxy.test.com:8080"
            assert os.environ.get("HTTPS_PROXY") == "http://proxy.test.com:8080"
            assert "NO_PROXY" in os.environ
            mock_install.assert_called_once_with("-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----")
