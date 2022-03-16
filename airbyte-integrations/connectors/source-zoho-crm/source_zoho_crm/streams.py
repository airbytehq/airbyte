import concurrent.futures
import logging
import requests
from abc import ABC
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.streams.http import HttpStream
from .api import ZohoAPI
from .exceptions import IncompleteMetaDataException, UnknownDataTypeException
from .types import ModuleMeta, FieldMeta, ZohoPickListItem


logger = logging.getLogger(__name__)


class ZohoCrmStream(HttpStream, ABC):
    json_schema = {}
    _path = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pagination = response.json()["info"]
        if not pagination["more_records"]:
            return None
        return {"page": pagination["page"] + 1}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return {**next_page_token}
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]

    def path(self, *args, **kwargs) -> str:
        return self._path

    def get_json_schema(self) -> Dict[Any, Any]:
        return self.json_schema


class ZohoStreamFactory:
    def __init__(self, config):
        self.api = ZohoAPI(config)

    def _init_modules_meta(self) -> List[ModuleMeta]:
        response = self.api.modules_settings()
        if not response.status_code == 200:
            return []
        modules_meta_json = response.json()["modules"]
        modules = [ModuleMeta.from_dict(module) for module in modules_meta_json]
        return list(filter(lambda module: module.api_supported, modules))

    def _populate_fields_meta(self, module: ModuleMeta):
        response = self.api.fields_settings(module.api_name)
        if not response.status_code == 200:
            logger.warning(f"{module} fields data inaccessible: HTTP status {response.status_code}")
            return
        fields_meta_json = response.json()["fields"]
        fields_meta = []
        for field in fields_meta_json:
            pick_list_values = field.get("pick_list_values", [])
            if pick_list_values:
                field["pick_list_values"] = [
                    ZohoPickListItem.from_dict(pick_list_item)
                    for pick_list_item in field["pick_list_values"]
                ]
            fields_meta.append(FieldMeta.from_dict(field))
        module.fields = fields_meta

    def _populate_module_meta(self, module: ModuleMeta):
        response = self.api.module_settings(module.api_name)
        if not response.status_code == 200:
            logger.warning(f"{module} meta data inaccessible: HTTP status {response.status_code}")
            return
        module_meta_json = response.json()["modules"]
        module_meta_json = next(iter(module_meta_json), None)
        module.update_from_dict(module_meta_json)

    def produce(self) -> List[HttpStream]:
        modules = self._init_modules_meta()
        streams = []

        def populate_module(module):
            self._populate_module_meta(module)
            self._populate_fields_meta(module)

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(modules)) as executor:
            executor.map(lambda module: populate_module(module), modules)

        for module in modules:
            try:
                schema = asdict(module.schema)
            except (IncompleteMetaDataException, UnknownDataTypeException):
                continue

            cls = type(
                f"{module.api_name}ZohoCRMStream",
                (ZohoCrmStream,),
                {
                    "url_base": f"{self.api.api_url}",
                    "_path": f"/crm/v2/{module.api_name}",
                    "json_schema": schema,
                    "primary_key": None
                }
            )
            # TODO: add Incremental streams
            # TODO: process rate limits and backoff policy
            streams.extend([cls(self.api.authenticator)])
        return streams
