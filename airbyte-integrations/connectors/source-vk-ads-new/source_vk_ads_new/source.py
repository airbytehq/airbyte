import json
from abc import ABC, abstractproperty
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import logging
import requests
from airbyte_cdk.models import SyncMode, ConnectorSpecification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests.auth import AuthBase
from source_vk_ads_new.auth import CredentialsCraftAuthenticator
from source_vk_ads_new.utils import chunks
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from source_vk_ads_new.fields import AVAILABLE_FIELDS
from airbyte_cdk.sources.streams.core import package_name_from_class

CONFIG_DATE_FORMAT = "%Y-%m-%d"


# Basic full refresh stream
class VkAdsNewStream(HttpStream, ABC):
    limit = 250
    url_base = "https://ads.vk.com/api/"
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)

    def __init__(self, authenticator: AuthBase = None):
        HttpStream.__init__(self)
        self._authenticator = authenticator

    def request_params(self, next_page_token: Mapping[str, Any] = {}, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            "limit": self.limit,
            "offset": next_page_token.get("offset", 0) if next_page_token else 0,
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data: dict[str, Any] = response.json()
        # ensure pagination objects are in response
        if all(key in ("count", "offset", "items") for key in response_data.keys()):
            if response_data.get("items") and len(response_data.get("items", [])) == self.limit:
                return {"offset": response_data.get("offset") + self.limit}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["items"]


class ObjectStream(VkAdsNewStream, ABC):
    primary_key = "id"
    use_cache = True

    def __init__(self, authenticator: AuthBase = None):
        super().__init__(authenticator=authenticator)
        self.spec_fields = None

    def path(self, *args, **kwargs) -> str:
        return f"v2/{self.many_objects_field_name}.json"

    @abstractproperty
    def single_object_field_name(self) -> str:
        raise NotImplementedError

    @property
    def spec_fields_field_name(self) -> str:
        return self.many_objects_field_name + "_stream_fields"

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        all_fields_schema: dict[str, Any] = schema["properties"].copy()
        schema["properties"] = {}
        for spec_field_name in self.build_fields():
            spec_field_schema = all_fields_schema.get(
                spec_field_name,
                {"type": ["string", "null"]},
            )
            schema["properties"][spec_field_name] = spec_field_schema
        return schema

    def build_fields(self) -> list[str]:
        available_fields = AVAILABLE_FIELDS[self.many_objects_field_name]
        fields = []
        all_fields = available_fields["required"] + available_fields["additional"]
        if self.spec_fields:
            if self.spec_fields["fields_spec_type"] == "all_available_fields":
                fields = all_fields
            elif self.spec_fields["fields_spec_type"] == "user_specified_fields":
                user_specified_fields = self.spec_fields["user_specified_fields"]
                for required_field in available_fields["required"]:
                    if required_field not in user_specified_fields:
                        raise ValueError(f'Stream {self.name} required fields: {available_fields["required"]}')
                fields = user_specified_fields
        return fields

    def request_params(
        self,
        next_page_token: Mapping[str, Any] = {},
        *args,
        **kwargs,
    ) -> MutableMapping[str, Any]:
        params = {
            **super().request_params(next_page_token, *args, **kwargs),
            "fields": ",".join(self.build_fields()),
        }
        return params

    @abstractproperty
    @classmethod
    def many_objects_field_name(self) -> str:
        raise NotImplementedError


class StatisticsStream(VkAdsNewStream, HttpSubStream, ABC):
    def __init__(
        self,
        *,
        authenticator: AuthBase = None,
        date_from: datetime,
        date_to: datetime,
        parent: ObjectStream,
    ):
        if not isinstance(parent, self.parent_class):
            raise ValueError(f"{self.name} can't be instantiated with {parent.name} class as substream parent")
        HttpSubStream.__init__(self, parent=parent)
        VkAdsNewStream.__init__(self, authenticator=authenticator)
        self.parent: ObjectStream = self.parent
        self.date_from = date_from
        self.date_to = date_to

    @abstractproperty
    def parent_class(self) -> VkAdsNewStream:
        raise NotImplementedError

    def path(self, *args, **kwargs) -> str:
        return f"v2/statistics/{self.parent.many_objects_field_name}/day.json"

    def request_params(self, stream_slice: Mapping[str, any] = {}, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            **VkAdsNewStream.request_params(self, stream_slice=stream_slice, *args, **kwargs),
            "date_from": self.date_from.strftime("%Y-%m-%d"),
            "date_to": self.date_to.strftime("%Y-%m-%d"),
            "metrics": "all",
            **stream_slice,
        }

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for ids_chunk in chunks(
            super().stream_slices(
                sync_mode=sync_mode,
                cursor_field=cursor_field,
                stream_state=stream_state,
            ),
            20,
        ):
            yield {"id": ",".join([str(parent_record["parent"]["id"]) for parent_record in ids_chunk])}

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, any] = {},
        *args,
        **kwargs,
    ) -> Iterable[Mapping]:
        for item in VkAdsNewStream.parse_response(
            self,
            response=response,
            stream_slice=stream_slice,
            *args,
            **kwargs,
        ):
            for row in item["rows"]:
                yield {
                    self.parent.single_object_field_name + "_id": item["id"],
                    **row,
                }


class AgencyClients(ObjectStream):
    single_object_field_name = "agency_client"
    many_objects_field_name = "agency/clients"


class Banners(ObjectStream):
    single_object_field_name = "banner"
    many_objects_field_name = "banners"


class AdPlans(ObjectStream):
    single_object_field_name = "ad_plan"
    many_objects_field_name = "ad_plans"


class AdGroups(ObjectStream):
    single_object_field_name = "ad_group"
    many_objects_field_name = "ad_groups"


class BannersStatistics(StatisticsStream):
    parent_class = Banners
    primary_key = ["banner_id", "date"]


class AdPlansStatistics(StatisticsStream):
    parent_class = AdPlans
    primary_key = ["ad_plan_id", "date"]


class AdGroupsStatistics(StatisticsStream):
    parent_class = AdGroups
    primary_key = ["ad_group_id", "date"]


# Source
class SourceVkAdsNew(AbstractSource):
    statistics_streams_classes: List[StatisticsStream] = [
        BannersStatistics,
        AdPlansStatistics,
        AdGroupsStatistics,
    ]
    object_streams_classes: List[ObjectStream] = [Banners, AdGroups, AdPlans]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth: Union[TokenAuthenticator, CredentialsCraftAuthenticator] = self.get_auth(config)

        if isinstance(auth, CredentialsCraftAuthenticator):
            success, message = auth.check_connection()
            if not success:
                return False, message

        streams: list[VkAdsNewStream] = self.streams(config)
        for stream in streams:
            stream.request_params()

        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        auth_type = config["credentials"]["auth_type"]
        if auth_type == "access_token_auth":
            return TokenAuthenticator(token=config["credentials"]["access_token"])
        elif auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                f"Invalid Auth type {auth_type}. Available: access_token_auth and credentials_craft_auth",
            )

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - timedelta(days=date_range["last_days_count"])
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(prepared_range["date_from"], CONFIG_DATE_FORMAT)

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(prepared_range["date_to"], CONFIG_DATE_FORMAT)
        config["prepared_date_range"] = prepared_range
        return config

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        properties: dict[str, Any] = spec.connectionSpecification["properties"]
        for property_order, obj_stream_class in enumerate(self.object_streams_classes, len(properties)):
            obj_stream: ObjectStream = obj_stream_class()
            available_fields = AVAILABLE_FIELDS[obj_stream.many_objects_field_name]
            properties[obj_stream.spec_fields_field_name] = {
                "type": "object",
                "title": f"{obj_stream_class.__name__} Stream Fields",
                "oneOf": [
                    {
                        "title": "User Specified Fields",
                        "type": "object",
                        "properties": {
                            "user_specified_fields": {
                                "title": "User Specified Fields",
                                "description": f"Field names that will be included in {obj_stream_class.__name__} stream schema. Required: {', '.join(available_fields['required'])}. See available schema fields: <a href=\"{available_fields['docs_url']}\">{obj_stream.single_object_field_name.title()} docs</a>",
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": available_fields["required"] + available_fields["additional"],
                                },
                                "default": available_fields["default"],
                            },
                            "fields_spec_type": {
                                "const": "user_specified_fields",
                                "type": "string",
                            },
                        },
                        "order": property_order,
                    },
                    {
                        "title": "All Available Fields",
                        "type": "object",
                        "properties": {
                            "fields_spec_type": {
                                "const": "all_available_fields",
                                "type": "string",
                            },
                        },
                        "order": property_order,
                    },
                ],
            }

        return spec

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.prepare_config_datetime(config)

        shared_kwargs = {"authenticator": auth}
        streams = []

        for statistics_stream_class in self.statistics_streams_classes:
            parent: ObjectStream = statistics_stream_class.parent_class(**shared_kwargs)
            parent.spec_fields = config.get(
                parent.spec_fields_field_name,
                {"fields_spec_type": "all_available_fields"},
            )
            streams.append(parent)
            streams.append(
                statistics_stream_class(
                    **shared_kwargs,
                    date_from=config["prepared_date_range"]["date_from"],
                    date_to=config["prepared_date_range"]["date_to"],
                    parent=parent,
                )
            )

        return streams
