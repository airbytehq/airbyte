# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Proxy config constants and helper functions."""

import os
import tempfile
from logging import Logger
from pathlib import Path


# Constants for proxy configuration keys
PROXY_PARENT_CONFIG_KEY = "http_proxy"
PROXY_URL_CONFIG_KEY = "proxy_url"
PROXY_CA_CERTIFICATE_CONFIG_KEY = "proxy_ca_certificate"


# Our hard-coded exclude list:
AIRBYTE_NO_PROXY_ENTRIES = [
    # Local and loopback
    "localhost",
    "127.0.0.1",
    "*.local",
    # Cloud metadata endpoints
    "169.254.169.254",  # Special link-local IP for metadata servers (AWS, Azure, etc.)
    "metadata.google.internal",  # GCP
    # Airbyte control/telemetry
    "*.airbyte.io",
    "*.airbyte.com",
    "connectors.airbyte.com",
    # Third-party telemetry
    "sentry.io",
    "api.segment.io",
    "*.sentry.io",
    "*.datadoghq.com",
    "app.datadoghq.com",
]


def _get_no_proxy_entries_from_env_var() -> list[str]:
    """Return a list of entries from the NO_PROXY environment variable."""
    if "NO_PROXY" in os.environ:
        return [x.strip() for x in os.environ["NO_PROXY"].split(",") if x.strip()]

    return []


def _get_no_proxy_string() -> str:
    """Return a string to be used as the NO_PROXY environment variable.

    This ensures that requests to these hosts bypass the proxy.
    """
    # Merge and dedupe our hardcoded list with any already-set `NO_PROXY` env var
    return ",".join(
        filter(
            None,  # Remove any None/Falsey values
            list(
                set(
                    # Combine and dedupe:
                    _get_no_proxy_entries_from_env_var() + AIRBYTE_NO_PROXY_ENTRIES
                )
            ),
        )
    )


def _install_ca_certificate(ca_cert_file_text: str) -> Path:
    """Install the CA certificate for the proxy.

    This involves saving the text to a local file and then setting
    the appropriate environment variables to use this certificate.

    Returns the path to the temporary CA certificate file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        prefix="airbyte-custom-ca-cert-",
        suffix=".pem",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(ca_cert_file_text)
        temp_file.flush()

    os.environ["REQUESTS_CA_BUNDLE"] = temp_file.name
    os.environ["CURL_CA_BUNDLE"] = temp_file.name
    os.environ["SSL_CERT_FILE"] = temp_file.name

    return Path(temp_file.name).absolute()


def configure_custom_http_proxy(
    http_proxy_config: dict[str, str],
    *,
    logger: Logger,
    proxy_url: str | None = None,
    ca_cert_file_text: str | None = None,
) -> None:
    """Initialize the proxy environment variables.

    If connector_config_dict is provided it contains an "http_proxy" entry, this config
    will be scanned for proxy config settings.

    If proxy_url and/or `ca_cert_file_text` are provided, they will override the values in
    connector_config_dict.

    The function will no-op if neither input option provides a proxy URL.
    """
    proxy_url = proxy_url or http_proxy_config.get(PROXY_URL_CONFIG_KEY)
    ca_cert_file_text = ca_cert_file_text or http_proxy_config.get(PROXY_CA_CERTIFICATE_CONFIG_KEY)

    if proxy_url:
        logger.info(f"Using custom proxy URL: {proxy_url}")

        if ca_cert_file_text:
            # Install the CA certificate if provided, and set CA-related env vars:
            cert_file_path = _install_ca_certificate(ca_cert_file_text)
            logger.info(f"Using custom installed CA certificate: {cert_file_path!s}")

        # Set the remaining proxy config env vars:
        os.environ["NO_PROXY"] = _get_no_proxy_string()
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
