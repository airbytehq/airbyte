#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from itertools import groupby
from typing import Optional, List, Tuple, NoReturn

import airbyte_api_client
import click
import yaml

from .apply.yaml_loaders import EnvVarLoader

API_HEADERS_YAML_FILE_INSTRUCTION = """
headers:
  - name: Authorization
    value: Basic dXNlcjpwYXNzd29yZA==
  - name: Content-Type
    value: application/json
""".strip()


@dataclass
class ApplicationHeader:
    name: Optional[str]
    value: Optional[str]

    def __post_init__(self):
        try:
            assert isinstance(self.name, str) and self.name
            assert isinstance(self.value, str) and self.value
        except AssertionError:
            raise AttributeError("Header name and value must be non empty string")
        self.name = self.name.strip()
        self.value = self.value.strip()

    def clean(self):
        return ApplicationHeader(
            name=self.name.strip(),
            value=self.value.strip()
        )


def deduplicate_api_headers(application_headers: List[ApplicationHeader]) -> List[ApplicationHeader]:
    sorted_headers = sorted(application_headers, key=lambda header: header.name)
    groups = groupby(sorted_headers, key=lambda header: header.name)
    unique_headers = [
        ApplicationHeader(
            name=header_name,
            value=sorted([header.value for header in group_headers])[0]
        ) for header_name, group_headers in groups]
    return unique_headers


class InvalidHeaderConfigurationFile(Exception):
    pass


def deserialize_file_based_headers(header_configuration_path: str) -> List[ApplicationHeader]:
    with open(header_configuration_path) as file:
        content = yaml.load(file, EnvVarLoader)

    headers = content.get("headers", None)

    if not headers:
        raise AttributeError("""
        Please provide valid configuration file, like below
        headers:
          - name: Authorization
            value: Basic dXNlcjpwYXNzd29yZA==
          - name: Content-Type
            value: application/json
        """)

    try:
        application_headers = [ApplicationHeader(header["name"], header["value"]) for header in headers]
    except KeyError:
        raise InvalidHeaderConfigurationFile("Headers must have name and value keys")

    return deduplicate_api_headers(application_headers)


def deseriliaze_opiton_based_headers(api_headers: List[Tuple[str, str]]) -> List[ApplicationHeader]:
    return deduplicate_api_headers([
        ApplicationHeader(header_name, header_value) for header_name, header_value in api_headers
    ])


def merge_api_headers(
        option_based_headers: List[ApplicationHeader],
        file_based_headers: List[ApplicationHeader]) -> List[ApplicationHeader]:
    """
    This function merges the HTTP headers parsed from the yam file and from the CLI option. Headers from CLI options override those defined
    in th file.
    :param option_based_headers:  headers which came from CLI options --api-headers
    :param file_based_headers: all application headers which were parsed from file --api-headers-file
    :return: the merged list of unique Http headers
    """

    merged_headers = {header.name: header for header in file_based_headers}
    for header in option_based_headers:
        merged_headers[header.name] = header

    return list(merged_headers.values())


def deserialize_api_headers(api_headers: Optional[List[Tuple[str, str]]], api_headers_file: Optional[str]) -> List[ApplicationHeader]:
    if api_headers and api_headers_file:
        click.echo("Passed api headers file and api headers at the same time, Overriding policy applied when priority of file is higher")

    argument_based_headers = []
    file_based_application_headers = []

    if api_headers:
        argument_based_headers = deseriliaze_opiton_based_headers(api_headers)

    if api_headers_file:
        file_based_application_headers = deserialize_file_based_headers(api_headers_file)

    api_headers_result = merge_api_headers(
        argument_based_headers, file_based_application_headers
    )

    return api_headers_result


def set_api_headers(api_client: airbyte_api_client.ApiClient, api_headers: List[ApplicationHeader]) -> NoReturn:
    for api_header in api_headers:
        try:
            api_client.set_default_header(api_header.name, api_header.value)
        except Exception as e:
            click.echo(f"Skipping applying configuration due to exception {e}")
