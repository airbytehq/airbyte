from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from .schema_fields import AD_IMAGES_DEFAULT_FIELDS, ADS_DEFAULT_FIELDS, CAMPAIGNS_DEFAULT_FIELDS

from .utils import chunks, concat_multiple_lists, find_by_key, get_unique


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
        *args,
        **kwargs,
    ):
        HttpStream.__init__(self, authenticator=auth)
        self.client_login = client_login
        self.user_defined_fields_params = kwargs[self.__class__.__name__.lower() + "_fields_params"]

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {}

    @staticmethod
    def paginate(data: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, limit_size: int = 10_000) -> Mapping[str, Any]:
        data["params"].update(
            {
                "Page": {"Limit": limit_size, "Offset": next_page_token.get("Offset") if next_page_token else 0},
            }
        )
        return data

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        headers = {}
        if self.client_login:
            headers.update({"Client-Login": self.client_login})
        return headers

    @property
    def request_fields_object(self):
        return self.user_defined_fields_params or self.default_fields_names

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

        yield from records


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
