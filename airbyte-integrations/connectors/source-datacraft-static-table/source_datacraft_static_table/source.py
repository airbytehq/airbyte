#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import csv
from abc import ABC
from ast import Dict
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_datacraft_static_table.auth import DatacraftAuth
from source_datacraft_static_table.utils import datacraft_type_to_json_type_map, normalize_url


class DatacraftStaticTableStream(HttpStream):
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization
    )

    @property
    def primary_key(self) -> Optional[str]:
        return self.user_primary_keys

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        user_url_base: str,
        datasource_id: Union[str, int],
        user_primary_keys: list[str],
        **kwargs,
    ):
        super().__init__(authenticator, **kwargs)
        self.user_url_base = normalize_url(user_url_base)
        self.user_primary_keys = user_primary_keys
        self.datasource_id = datasource_id

        self.datasource = self.get_datasource()
        if not self.datasource.get("current_static_table_version"):
            raise Exception("Datasource has no static table version")
        self.current_static_table_version = self.datasource["current_static_table_version"]

    @property
    def url_base(self) -> str:
        return self.user_url_base

    def path(self, **kwargs) -> str:
        return f"/api/v1/datacraft_datasource/{self.datasource['id']}/static_table_version/{self.current_static_table_version['id']}/file"

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        properties = schema["properties"]
        for column in self.current_static_table_version["columns"]:
            properties[column["name"]] = {
                "type": [datacraft_type_to_json_type_map[column["type"]], "null"]
            }
        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        reader = csv.DictReader(response.iter_lines(decode_unicode=True))
        for row in reader:
            yield {k: v if v != "" else None for k, v in row.items()}

    def get_datasource(self) -> Mapping[str, Any]:
        url = self.user_url_base + "/api/v1/datacraft_datasource/" + str(self.datasource_id)
        response = requests.get(url, headers=self.authenticator.get_auth_header())
        if response.status_code != 200:
            if response.status_code == 404:
                raise Exception("Datasource not found")
            raise Exception("Error fetching datasource")
        data = response.json()["result"]
        if data["platform"] != "STATIC_TABLE":
            raise Exception(
                "Datasource type is not STATIC_TABLE. It is"
                f" '{data['platform']}'.Please select a STATIC_TABLE datasource."
            )
        return data


# Source
class SourceDatacraftStaticTable(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            stream = self.streams(config)[0]
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        except Exception as e:
            return False, f"Unable to connect to Datacraft: {e}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = DatacraftAuth(
            user_url_base=config["url_base"],
            username=config["username"],
            password=config["password"],
        )
        return [
            DatacraftStaticTableStream(
                auth,
                user_url_base=config["url_base"],
                datasource_id=config["datasource_id"],
                user_primary_keys=config.get("user_primary_keys"),
            )
        ]
