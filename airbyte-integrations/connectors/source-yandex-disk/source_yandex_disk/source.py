#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from cgi import test
import csv
import io
import json
import logging
import re
from abc import ABC
from datetime import datetime
from functools import cache
from typing import Any, Dict, Iterable, List, Literal, Mapping, MutableMapping, Optional, Tuple

import pandas as pd
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_yandex_disk.auth import CredentialsCraftAuthenticator

logger = logging.getLogger('airbyte')

# Basic full refresh stream


class YandexDiskResource(HttpStream, ABC):
    url_base = "https://downloader.disk.yandex.ru/disk/"
    primary_key = []
    limit = 1000
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        stream_name: str,
        resources_path: str,
        resources_filename_pattern: re.Pattern,
        resource_files_type: Literal['CSV', 'Excel'],
        excel_sheet_name: str,
        client_name_constant: str,
        product_name_constant: str,
        custom_constants: Dict[str, Any],
        user_specified_fields: List[str] = [],
        csv_delimiter: str = None,
        no_header: bool = False,
        date_from: datetime = None,
        date_to: datetime = None,
    ) -> None:
        super().__init__(authenticator=authenticator)
        self.stream_name = stream_name
        self.resources_path = resources_path
        self.resources_filename_pattern = re.compile(
            resources_filename_pattern)
        self.resource_files_type = resource_files_type
        self.date_from = date_from
        self.date_to = date_to
        self.product_name_constant = product_name_constant
        self.client_name_constant = client_name_constant
        self.custom_constants = custom_constants
        self.excel_sheet_name = excel_sheet_name
        self._authenticator = authenticator
        self.csv_delimiter = csv_delimiter
        self.no_header = no_header
        self.user_specified_fields = user_specified_fields

    @property
    def name(self) -> str:
        return self.stream_name

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(
            self.__class__)).get_schema("yandex_disk_resource")

        if self.user_specified_fields:
            fields = self.user_specified_fields
        else:
            fields = self.derive_fields_names_from_sample()

        for field_name in fields:
            schema["properties"][field_name] = {"type": ["null", "string"]}

        extra_properties = ["__productName", "__clientName"]
        extra_properties.extend(self.custom_constants.keys())

        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {}

    def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        return stream_slice['href']

    def parse_csv_response(self, response: requests.Response) -> Iterable[Mapping]:
        lines_gen = (line.decode("utf-8").replace('\ufeff', '')
                     for line in response.iter_lines())

        if self.csv_delimiter:
            lines_reader = csv.reader(lines_gen, delimiter=self.csv_delimiter)
        else:
            lines_reader = csv.reader(lines_gen)
        if not self.no_header:
            if self.user_specified_fields:
                next(lines_reader)
                headers = self.user_specified_fields
            else:
                headers = next(lines_reader)
        else:
            headers = self.user_specified_fields

        for values_line_n, values_line in enumerate(lines_reader):
            if values_line_n == 0:
                if self.user_specified_fields and len(values_line) != len(self.user_specified_fields):
                    if len(values_line) == 0:
                        continue
                    raise Exception(
                        f'Stream {self.stream_name} user_specified_fields'
                        ' count doesn\'t equals to files columns count. '
                        '(user_specified_fields count - '
                        f'{len(self.user_specified_fields)}, columns '
                        f'count - {len(values_line)}).'
                    )
            record = dict(zip(headers, values_line))
            if record:
                yield self.add_constants_to_record(record)

    def parse_excel_response(self, response: requests.Response) -> Iterable[Mapping]:
        with io.BytesIO(response.content) as fh:
            read_excel_kwargs = {
                "sheet_name": self.excel_sheet_name if self.excel_sheet_name else 0
            }

            if self.no_header:
                read_excel_kwargs['header'] = None
                read_excel_kwargs['names'] = self.user_specified_fields
            else:
                if self.user_specified_fields:
                    read_excel_kwargs['names'] = self.user_specified_fields

            df = pd.io.excel.read_excel(fh, **read_excel_kwargs)
            for record in df.to_dict('records'):
                yield self.add_constants_to_record(record)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if self.resource_files_type == 'CSV':
            yield from self.parse_csv_response(response)
        elif self.resource_files_type == 'Excel':
            yield from self.parse_excel_response(response)
        else:
            raise Exception(
                f'Unsupported file type: {self.resource_files_type}')

    def add_constants_to_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        constants = {
            "__productName": self.product_name_constant,
            "__clientName": self.client_name_constant,
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def request_kwargs(self, *args, **kwargs) -> Mapping[str, Any]:
        request_kwargs: Dict = super().request_kwargs(*args, **kwargs)
        request_kwargs.update({"stream": True})
        return request_kwargs

    def get_path_resources(self):
        available_resources = []
        offset = 0
        while True:
            resources_response = requests.get(
                url='https://cloud-api.yandex.net/v1/disk/resources',
                params={
                    'path': self.resources_path,
                    'limit': self.limit,
                    'offset': offset,
                    'sort': '-created'
                },
                headers=self.authenticator.get_auth_header()
            )
            try:
                resources_response.raise_for_status()
            except:
                raise Exception(
                    f'Api Error {resources_response.status_code}: {resources_response.text}. URL {resources_response.request.url}')
            resources_response_items = resources_response.json()[
                '_embedded'].get('items')
            available_resources = [
                *available_resources,
                *resources_response_items
            ]
            if len(resources_response_items) < self.limit:
                break
            offset += self.limit
        return available_resources

    @cache
    def derive_fields_names_from_sample(self):
        sample_file = self.lookup_resources_for_pattern()[0]
        download_file_link = self.get_download_link_for_resource(sample_file)[
            'href']
        sample_record: Dict[str, Any] = next(self.parse_response(
            requests.get(
                download_file_link,
                headers=self.authenticator.get_auth_header()
            )
        ))
        fields = sample_record.keys()
        print(f'Fields for stream {self.name}: {fields}')
        logger.info(f'Fields for stream {self.name}: {fields}')
        return fields

    @cache
    def lookup_resources_for_pattern(self):
        resources = []
        for resource in filter(lambda r: r['type'] == 'file', self.get_path_resources()):
            if self.resources_filename_pattern.match(resource['name']):
                resources.append(resource)
        logger.info(
            f'Stream {self.name}: found resources for pattern'
            f' {self.resources_filename_pattern}:'
            f' {[resource["path"] for resource in resources]}'
        )
        return resources

    def get_download_link_for_resource(self, resource):
        download_link_response = requests.get(
            url='https://cloud-api.yandex.net/v1/disk/resources/download',
            params={
                'path': resource['path']
            },
            headers=self.authenticator.get_auth_header()
        )
        download_link_response.raise_for_status()
        download_link_obj = download_link_response.json()
        logger.info(
            f'Stream {self.name}: download link for resource'
            f' {resource["path"]} - {download_link_obj["href"]}'
        )
        return download_link_obj

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for resource in self.lookup_resources_for_pattern():
            file = self.get_download_link_for_resource(resource)
            file['href'] = file['href'].replace(self.url_base, '')
            yield file


class SourceYandexDisk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            json.loads(config.get("custom_constants_json", "{}"))
        except Exception as msg:
            return False, f"Invalid Custom Constants JSON: {msg}"

        for stream_config in config['streams']:
            if stream_config.get('no_header', False) and not stream_config.get('user_specified_fields'):
                return False, f'"No Header" selected for stream {stream_config["name"]},' + \
                    ' but no user_specified_fields specified.'

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            cc_auth_check_result = auth.check_connection()
            if not cc_auth_check_result[0]:
                return cc_auth_check_result

        test_stream_config = config['streams'][0]
        test_request = requests.get(
            'https://cloud-api.yandex.net/v1/disk/resources',
            headers=auth.get_auth_header(),
            params={
                'path': test_stream_config['path']
            }
        )
        try:
            test_request.raise_for_status()
        except:
            raise Exception(
                f'Api Error {test_request.status_code}: {test_request.text}. URL {test_request.request.url}')

        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(
                token=config["credentials"]["access_token"],
                auth_method='OAuth'
            )
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                "Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def transform_config(self, config: dict[str, Any]) -> dict[str, Any]:
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_auth(config)
        config = self.transform_config(config)
        streams = []
        logger.info(f'Streams: {config["streams"]}')

        for stream_config in config['streams']:
            user_specified_fields = stream_config.get(
                'user_specified_fields', '').strip().split(',')
            if user_specified_fields == ['']:
                user_specified_fields = None
            streams.append(
                YandexDiskResource(
                    authenticator=authenticator,
                    stream_name=stream_config['name'],
                    resources_path=stream_config['path'],
                    resources_filename_pattern=stream_config['files_pattern'],
                    resource_files_type=stream_config['files_type'],
                    excel_sheet_name=stream_config.get('excel_sheet_name'),
                    client_name_constant=config['client_name_constant'],
                    product_name_constant=config['product_name_constant'],
                    custom_constants=json.loads(
                        config.get('custom_constants_json', '{}')
                    ),
                    user_specified_fields=user_specified_fields,
                    csv_delimiter=stream_config.get('csv_delimiter'),
                    no_header=stream_config.get('no_header'),
                )
            )
        return streams
