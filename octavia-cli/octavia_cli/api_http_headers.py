#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import List, Optional, Tuple

import airbyte_api_client
import click
import yaml

from .apply.yaml_loaders import EnvVarLoader
from .init.commands import API_HTTP_HEADERS_TARGET_PATH


class InvalidApiHttpHeadersFileError(click.exceptions.ClickException):
    pass


@dataclass
class ApiHttpHeader:
    name: str
    value: str

    def __post_init__(self):
        try:
            assert isinstance(self.name, str) and self.name
            assert isinstance(self.value, str) and self.value
        except AssertionError:
            raise AttributeError("Header name and value must be non empty string.")
        self.name = self.name.strip()
        self.value = self.value.strip()


def deserialize_file_based_headers(header_configuration_path: str) -> List[ApiHttpHeader]:
    """Parse API HTTP headers declared in a YAML file to a list of ApiHttpHeaders

    Args:
        header_configuration_path (str): Path to the YAML file where API HTTP headers are declared.

    Raises:
        InvalidApiHttpHeadersFileError: Raised if the YAML structure is not valid.

    Returns:
        List[ApiHttpHeader]: List of HTTP headers parsed from the YAML file.
    """
    with open(header_configuration_path) as file:
        try:
            content = yaml.load(file, EnvVarLoader)
            headers = content["headers"]
        except (TypeError, KeyError, yaml.scanner.ScannerError):
            raise InvalidApiHttpHeadersFileError(
                f"Please provide valid yaml file to declare API HTTP headers. Please check the {API_HTTP_HEADERS_TARGET_PATH} file."
            )

    return [ApiHttpHeader(name, value) for name, value in headers.items()]


def deserialize_option_based_headers(api_http_headers: List[Tuple[str, str]]) -> List[ApiHttpHeader]:
    """Parse API HTTP headers declared in CLI options to a list of ApiHttpHeaders

    Args:
        api_http_headers (List[Tuple[str, str]]): Raw list of api headers tuples retrieved from CLI options.

    Returns:
        List[ApiHttpHeader]: List of HTTP headers parsed from the CLI options.
    """
    return list({header_name: ApiHttpHeader(header_name, header_value) for header_name, header_value in api_http_headers}.values())


def merge_api_headers(
    option_based_api_http_headers: Optional[List[Tuple[str, str]]], api_http_headers_file_path: Optional[str]
) -> List[ApiHttpHeader]:
    """Deserialize headers from options and files into ApiHttpHeader and merge options based headers with file based headers.

    Args:
        option_based_api_http_headers (Optional[List[Tuple[str, str]]]): Option based headers.
        api_http_headers_file_path (Optional[str]): Path to the YAML file with http headers.

    Returns:
        List[ApiHttpHeader]: Lit of unique ApiHttpHeaders
    """
    if option_based_api_http_headers and api_http_headers_file_path:
        click.echo(
            "ℹ️  - You passed API HTTP headers in a file and in options at the same time. Option based headers will override file based headers."
        )
    option_based_headers = (
        deserialize_option_based_headers(option_based_api_http_headers) if option_based_api_http_headers is not None else []
    )
    file_based_headers = deserialize_file_based_headers(api_http_headers_file_path) if api_http_headers_file_path else []

    merged_headers = {header.name: header for header in file_based_headers}
    for header in option_based_headers:
        merged_headers[header.name] = header
    return list(merged_headers.values())


def set_api_headers_on_api_client(api_client: airbyte_api_client.ApiClient, api_headers: List[ApiHttpHeader]) -> None:
    """Set the API headers on the API client

    Args:
        api_client (airbyte_api_client.ApiClient): The API client on which headers will be set.
        api_headers (List[ApiHttpHeader]): Headers to set on the API client.
    """
    for api_header in api_headers:
        api_client.set_default_header(api_header.name, api_header.value)
