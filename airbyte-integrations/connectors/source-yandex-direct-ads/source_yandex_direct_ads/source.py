#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_yandex_direct_ads.fields import AD_IMAGES_DEFAULT_FIELDS, ADS_DEFAULT_FIELDS, CAMPAIGNS_DEFAULT_FIELDS

from .auth import CredentialsCraftAuthenticator
from .utils import chunks, concat_multiple_lists, find_by_key, get_unique


# Basic full refresh stream
class YandexDirectAdsStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)
    url_base = "https://api.direct.yandex.com/json/v5/"
    http_method = "POST"
    primary_key = "Id"
    limit_size = 10_000
    default_fields_names = None

    def __init__(
        self,
        auth: TokenAuthenticator,
        client_login: str,
        client_name: str = None,
        product_name: str = None,
        custom_constants: str = "{}",
        *args,
        **kwargs,
    ):
        HttpStream.__init__(self, authenticator=auth)
        self.client_login = client_login
        self.client_name = client_name
        self.product_name = product_name
        self.custom_constants = custom_constants
        self.user_defined_fields_params = kwargs[self.__class__.__name__.lower() + "_fields_params"]

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {}

    @staticmethod
    def paginate(data: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, limit_size: int = 10_000) -> Mapping[str, Any]:
        data["params"].update({"Page": {"Limit": limit_size, "Offset": next_page_token.get("Offset") if next_page_token else 0}})
        return data

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        headers = {}
        if self.client_login:
            headers.update({"Client-Login": self.client_login})
        return headers

    @property
    def request_fields_object(self):
        return self.user_defined_fields_params or self.default_fields_names

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.product_name,
            "__clientName": self.client_name,
        }
        constants.update(json.loads(self.custom_constants))
        record.update(constants)
        return record

    def get_json_schema(self):
        schema: dict = super().get_json_schema()
        default_schema_properties = schema["properties"].copy()
        schema["properties"] = {}
        if self.user_defined_fields_params:
            for key in self.user_defined_fields_params:

                if key == "FieldNames":
                    for top_level_field in self.user_defined_fields_params[key]:
                        schema["properties"][top_level_field] = default_schema_properties[top_level_field]
                    continue
                key = key.replace("FieldNames", "")

                try:
                    default_schema_properties[key]
                except:
                    continue

                schema["properties"][key] = {"type": ["null", "object"], "properties": {}}
                for inner_level_field in self.user_defined_fields_params[key + "FieldNames"]:
                    schema["properties"][key]["properties"][inner_level_field] = default_schema_properties[key]["properties"][
                        inner_level_field
                    ]
        else:
            schema["properties"] = default_schema_properties
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.custom_constants).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if data.get("LimitedBy"):
            return {"Offset": data.get("LimitedBy")}

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        self.logger.info(f"Request {response.request.url} (Headers: {response.request.headers}, body {response.request.body})")
        if "result" not in data.keys():
            raise Exception(f"URL: {response.url} ({response.request.body}). ApiError: {data}")
        records = data["result"].get(self.__class__.__name__, [])

        yield from map(self.add_constants_to_record, records)


class DependsOnParentIdsSubStream(HttpSubStream, ABC):
    parent_ids_slices_chunk_size = 10
    depends_on_object_keys_path = ["Id"]

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_records = list(HttpSubStream.stream_slices(self, *args, **kwargs))
        slices = []
        for chunk in chunks(parent_records, self.parent_ids_slices_chunk_size):
            parent_records_ids_chunk = []
            for parent_record in chunk:
                parent_record = parent_record["parent"]
                extracted_obj = parent_record
                for key in self.depends_on_object_keys_path:
                    extracted_obj = extracted_obj[key]
                parent_records_ids_chunk.append(extracted_obj)
            slices.append({"parent_records_ids": parent_records_ids_chunk})
        return slices


class Campaigns(YandexDirectAdsStream):
    use_cache = True
    default_fields_names = CAMPAIGNS_DEFAULT_FIELDS

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, *args, **kwargs) -> Optional[Mapping]:
        request_object = {
            "method": "get",
            "params": {"SelectionCriteria": {}, **self.request_fields_object},
        }
        body = self.paginate(
            request_object,
            next_page_token,
        )
        return body

    def path(self, *args, **kwargs) -> str:
        return "campaigns"


class Ads(YandexDirectAdsStream, DependsOnParentIdsSubStream):
    default_fields_names = ADS_DEFAULT_FIELDS

    def __init__(self, *args, **kwargs):
        DependsOnParentIdsSubStream.__init__(self, Campaigns(*args, **kwargs))
        YandexDirectAdsStream.__init__(self, *args, **kwargs)

    def path(self, *args, **kwargs) -> str:
        return "ads"

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = {}, next_page_token: Mapping[str, Any] = None, *args, **kwargs
    ) -> Optional[Mapping]:
        current_campaign_ids = stream_slice.get("parent_records_ids", [])
        request_object = {
            "method": "get",
            "params": {"SelectionCriteria": {"CampaignIds": current_campaign_ids}, **self.request_fields_object},
        }
        body = self.paginate(
            request_object,
            next_page_token,
        )
        return body


class AdImages(YandexDirectAdsStream, DependsOnParentIdsSubStream):
    primary_key = "AdImageHash"
    default_fields_names = AD_IMAGES_DEFAULT_FIELDS

    def __init__(self, use_simple_loader: bool = False, *args, **kwargs):
        DependsOnParentIdsSubStream.__init__(self, Ads(*args, **kwargs))
        YandexDirectAdsStream.__init__(self, *args, **kwargs)
        self.use_simple_loader = use_simple_loader

    def path(self, *args, **kwargs) -> str:
        return "adimages"

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = {}, next_page_token: Mapping[str, Any] = None, *args, **kwargs
    ) -> Optional[Mapping]:
        current_ad_image_hashes = stream_slice.get("parent_records_ids", []) if stream_slice else []
        request_object = {
            "method": "get",
            "params": {"SelectionCriteria": {"AdImageHashes": current_ad_image_hashes}, **self.request_fields_object},
        }
        if self.use_simple_loader:
            request_object["params"]["SelectionCriteria"] = {}
        body = self.paginate(
            request_object,
            next_page_token,
        )
        return body

    def stream_slices(
        self, *, sync_mode: SyncMode = None, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.use_simple_loader:
            yield from [{}]
            return
        parent_records = [record["parent"] for record in HttpSubStream.stream_slices(self, sync_mode, cursor_field, stream_state)]
        ad_image_hashes = [list(find_by_key(record, "AdImageHash")) for record in parent_records]
        ad_image_hashes_not_null = [[hash for hash in hashes if hash] for hashes in ad_image_hashes]
        for ad_images_hashes_chunk in chunks(get_unique(concat_multiple_lists(ad_image_hashes_not_null)), 10):
            yield {"parent_records_ids": ad_images_hashes_chunk}


# Source
class SourceYandexDirectAds(AbstractSource):
    streams_classes = [Ads, AdImages, Campaigns]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            json.loads(config.get("custom_constants", "{}"))
        except:
            return False, "Invalid Custom Constants"

        spec_fields_names_for_streams = self.get_spec_fields_names_for_streams(self.streams_classes)
        for stream_class, spec_field_name in spec_fields_names_for_streams:
            try:
                json.loads(config.get(spec_field_name, "{}"))
            except:
                return False, f"Invalid JSON in {spec_field_name}. See example."
            if not config.get(spec_field_name):
                continue
            stream_class_default_fields = stream_class.default_fields_names
            stream_fields_params_from_config = json.loads(config[spec_field_name])
            if not isinstance(stream_class_default_fields, dict):
                return False, f"{spec_field_name} is not of valid structire. It must be object of field names. See example."
            for key in stream_fields_params_from_config:
                if key not in stream_class_default_fields:
                    return False, f"{spec_field_name}: Key {key} is not available for this stream params customization. See example."
                key_default_fields_list = stream_class_default_fields[key]
                config_key_fields_list = stream_fields_params_from_config[key]
                for field_name in config_key_fields_list:
                    if field_name not in key_default_fields_list:
                        return False, f'{spec_field_name} (key {key}): field "field_name" is not available. See example.'

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        json_data_obj = {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": [
                    "Id",
                ],
                "Page": {"Limit": 1, "Offset": 0},
            },
        }
        headers = auth.get_auth_header()
        if config.get("client_login"):
            headers.update({"Client-Login": config.get("client_login")})
        response = requests.post("https://api.direct.yandex.com/json/v5/campaigns", json=json_data_obj, headers=headers)
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            return False, f"Text: {response.text}. Code: {response.status_code}. Headers: {response.headers}"

        if "error" in response_data.keys():
            return False, response_data["error"]["error_detail"]
        if "result" in response_data.keys():
            return True, None

    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception("Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        properties = spec.connectionSpecification["properties"]
        extra_spec_fields = self.generate_spec_fields_for_streams(self.streams_classes)

        for property_order, property_key in enumerate(extra_spec_fields, len(properties)):
            new_property = extra_spec_fields[property_key]
            new_property["order"] = property_order
            properties[property_key] = new_property

        return spec

    def generate_spec_fields_for_streams(self, streams_classes: List[YandexDirectAdsStream]) -> List[Mapping[str, Any]]:
        streams_spec_fields = {}
        for stream_class in streams_classes:
            spec_field = {
                "description": f"{stream_class.__name__} stream fields params. Leave empty for default.",
                "title": f"{stream_class.__name__} Stream Fields Params (Optional)",
                "type": "string",
                "examples": ['{"FieldNames": ["CampaignId", "Id"], "MobileAppAdFieldNames": ["Text", "Title"]}'],
                "order": 4,
            }
            streams_spec_fields[stream_class.__name__.lower() + "_fields_params"] = spec_field
        return streams_spec_fields

    def get_spec_fields_names_for_streams(self, streams: List[YandexDirectAdsStream]) -> List[Tuple[YandexDirectAdsStream, str]]:
        for stream in streams:
            yield (stream, stream.__name__.lower() + "_fields_params")

    def get_spec_property_name_for_stream(self, stream: YandexDirectAdsStream) -> Mapping[str, Any]:
        for stream_class, spec_field_name in self.get_spec_fields_names_for_streams(self.streams_classes):
            if stream.__name__ == stream_class.__name__:
                return spec_field_name

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)

        streams = []
        for stream_class in self.streams_classes:
            stream_kwargs = {
                "auth": auth,
                "client_login": config.get("client_login"),
                "client_name": config.get("client_name", ""),
                "product_name": config.get("product_name", ""),
                "custom_constants": config.get("custom_constants", "{}"),
            }
            if stream_class == AdImages:
                stream_kwargs["use_simple_loader"] = config.get("adimages_use_simple_loader", False)
            for _, spec_fields_name in self.get_spec_fields_names_for_streams(self.streams_classes):
                stream_kwargs[spec_fields_name] = json.loads(config.get(spec_fields_name, "{}"))
            streams.append(stream_class(**stream_kwargs))

        return streams
