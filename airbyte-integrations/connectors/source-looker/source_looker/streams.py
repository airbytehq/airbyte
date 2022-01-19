#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
import functools
import pendulum
import re
import requests
from abc import ABC
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from collections import defaultdict
from datetime import datetime
from enum import Enum
from jsonschema import Draft7Validator, validators
from prance import ResolvingParser
from requests.auth import AuthBase
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Callable, Dict
from urllib.parse import parse_qsl, urlparse

API_VERSION = "3.1"


class TypeTransformer2(TypeTransformer):

    def __init__(self, config: TransformConfig):
        if TransformConfig.NoTransform in config and config != TransformConfig.NoTransform:
            raise Exception("NoTransform option cannot be combined with other flags.")
        self._config = config
        all_validators = {
            key: self.__get_normalizer(key, orig_validator)
            for key, orig_validator in Draft7Validator.VALIDATORS.items()
            # Do not validate field we do not transform for maximum performance.
            if key in ["type", "array", "$ref", "properties", "items"]
        }
        self._normalizer = validators.create(meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators)

    def __get_normalizer(self, schema_key: str, original_validator: Callable):
        def normalizator(validator_instance: Callable, property_value: Any, instance: Any, schema: Dict[str, Any]):
            def resolve(subschema):
                if "$ref" in subschema:
                    _, resolved = validator_instance.resolver.resolve(subschema["$ref"])
                    return resolved
                return subschema

            # Transform object and array values before running json schema type checking for each element.
            if schema_key == "properties":
                for k, subschema in property_value.items():
                    if k in (instance or {}):
                        subschema = resolve(subschema)
                        try:
                            instance[k] = self.__normalize(instance[k], subschema)
                        except Exception as e:
                            raise Exception("SSSSS %s ## %s -> %s" % (e, k, instance))
            elif schema_key == "items":
                subschema = resolve(property_value)
                for index, item in enumerate((instance or [])):
                    instance[index] = self.__normalize(item, subschema)

            # Running native jsonschema traverse algorithm after field normalization is done.
            yield from original_validator(validator_instance, property_value, instance, schema)

        return normalizator

    def __normalize(self, original_item: Any, subschema: Dict[str, Any]) -> Any:
        if TransformConfig.DefaultSchemaNormalization in self._config:
            original_item = self.default_convert(original_item, subschema)

        if self._custom_normalizer:
            original_item = self._custom_normalizer(original_item, subschema)
        return original_item

    @staticmethod
    def normalizator(validator_instance, property_value, instance, schema):
        try:
            return super().normalizator(validator_instance, property_value, instance, schema)
        except:
            raise Exception("SSSSS %s -> %s" % ("aaa", instance))


CUSTOM_STREAM_NAMES = {
    "/projects/{project_id}/files": "project_files",
    "/roles/{role_id}/groups": "role_groups",
    "/groups": "groups",
    "/groups/{group_id}/groups": "group_groups",
    "/user_attributes/{user_attribute_id}/group_values": "user_attribute_group_values",
    "/users/{user_id}/attribute_values": "user_attribute_values",
    "/users/{user_id}/sessions": "user_sessions",
    "/dashboards": "dashboards",
    "/roles": "roles",
    "/users/{user_id}/roles": "user_roles",
    "/spaces/{space_id}/dashboards": "space_dashboards",
    "/folders/{folder_id}/dashboards": "folder_dashboards",
    "/content_metadata/{content_metadata_id}": "content_metadata",
    "/looks": "looks",
    "/folders/{folder_id}/looks": "folder_looks",
    "/spaces/{space_id}/looks": "space_looks",
    "/looks/search": "search_looks",
    "/looks/{look_id}": "look_info",
    "/lookml_models/{lookml_model_name}/explores/{explore_name}": "explore_models",
    "/dashboards/{dashboard_id}/dashboard_layouts": "dashboard_layouts",
    "/folders/{folder_id}/ancestors": "folder_ancestors",
    "/spaces/{space_id}/ancestors": "space_ancestors",
    "/groups/{group_id}/users": "group_users",
    "/users": "users",
    "/roles/{role_id}/users": "role_users",
}

FIELD_TYPE_MAPPING = {
    "string": "string",
    "date_date": "date",
    "date_raw": "string",
    "date": "date",
    "date_week": "date",
    "date_day_of_week": "string",
    "date_day_of_week_index": "integer",
    "date_month": "string",
    "date_month_num": "integer",
    "date_month_name": "string",
    "date_day_of_month": "integer",
    "date_fiscal_month_num": "integer",
    "date_quarter": "string",
    "date_quarter_of_year": "string",
    "date_fiscal_quarter": "string",
    "date_fiscal_quarter_of_year": "string",
    "date_year": "integer",
    "date_day_of_year": "integer",
    "date_week_of_year": "integer",
    "date_fiscal_year": "integer",
    "date_time_of_day": "string",
    "date_hour": "string",
    "date_hour_of_day": "integer",
    "date_minute": "string",
    "date_second": "date-time",
    "date_millisecond": "date-time",
    "date_microsecond": "date-time",
    "number": "number",
    "int": "integer",
    "list": "array",
    "yesno": "boolean",
}


class LookerException(Exception):
    pass


class BaseLookerStream(HttpStream, ABC):
    primary_key = None
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, *, domain: str, **kwargs):
        self._domain = domain
        super().__init__(**kwargs)

    @property
    def authenticator(self):
        if self._session.auth:
            return self._session.auth
        return super().authenticator

    @property
    def url_base(self):
        return f"https://{self._domain}/api/{API_VERSION}/"

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        return None


class SwaggerParser(BaseLookerStream):
    class Endpoint:
        def __init__(self, *, name: str, path: str, schema: Mapping[str, Any], operation_id: str, summary: str):
            self.name, self.path, self.schema, self.operation_id, self.summary = name, path, schema, operation_id, summary

    def path(self, **kwargs: Any):
        return "swagger.json"

    def parse_response(self, response: requests.Response, **kwargs: Any) -> Iterable[Mapping]:
        yield ResolvingParser(spec_string=response.text)

    @functools.lru_cache(maxsize=None)
    def get_endpoints(self):
        parser = next(self.read_records(sync_mode=None))
        endpoints = {}
        for path, methods in parser.specification["paths"].items():
            if not methods.get("get") or not methods["get"]["responses"].get("200"):
                continue
            get_data = methods["get"]
            parts = path.split("/")
            # self.logger.warning("dddddd %s" % path)
            name = CUSTOM_STREAM_NAMES.get(path)
            if not name:
                name = "/".join(parts[-2:]) if parts[-1].endswith("}") else parts[-1]
            if path == "/content_metadata_access":
                path += "?content_metadata_id={content_metadata_id}"

            schema = get_data["responses"]["200"]["schema"]
            endpoints[name] = self.Endpoint(name=name, path=path,
                                            schema=self.format_schema(schema),
                                            summary=get_data["summary"],
                                            operation_id=get_data["operationId"])

        # stream "lookml_dashboards" uses same endpoints
        # "lookml_dashboards" and "dashboards" have one different only:
        # "id" of "dashboards" is integer
        # "id" of "lookml_dashboards" is string
        dashboards_schema = endpoints["dashboards"].schema
        lookml_dashboards_schema = copy.deepcopy(dashboards_schema)
        dashboards_schema["items"]["properties"]["id"]["type"] = "integer"
        lookml_dashboards_schema["items"]["properties"]["id"]["type"] = "string"
        endpoints["lookml_dashboards"] = self.Endpoint(
            name="lookml_dashboards", path=endpoints["dashboards"].path,
            schema=lookml_dashboards_schema,
            summary=endpoints["dashboards"].summary,
            operation_id=endpoints["dashboards"].operation_id)
        return endpoints

    @classmethod
    def format_schema(cls, schema: Mapping[str, Any], key: str = None) -> Mapping[str, Any]:

        updated_schema = {}
        if "properties" in schema:
            schema["type"] = ["null", "object"]
            updated_sub_schemas = {}
            for key, sub_schema in schema["properties"].items():
                updated_sub_schemas[key] = cls.format_schema(sub_schema, key=key)
            updated_schema["properties"] = updated_sub_schemas

        elif "items" in schema:
            schema["type"] = ["null", "array"]
            updated_schema["items"] = cls.format_schema(schema["items"])

        if "format" in schema:
            if schema["format"] == "int64" and (not key or not key.endswith("id")):
                updated_schema["multipleOf"] = 10 ** -16
                schema["type"] = ["null", "number"]
            else:
                updated_schema["format"] = schema["format"]
        if "description" in schema:
            updated_schema["description"] = schema["description"]
        if schema.get("x-looker-nullable") is True and isinstance(schema["type"], str):
            schema["type"] = ["null", schema["type"]]
        updated_schema["type"] = schema["type"]
        return updated_schema


class LookerStream(BaseLookerStream, ABC):
    parent_slice_key = "id"
    slice_key = None

    def __init__(self, name: str, swagger_parser: SwaggerParser, request_params: Mapping[str, Any] = None, **kwargs):
        self._swagger_parser = swagger_parser
        self._name = name
        # raise LookerException(request_params)
        self._request_params = request_params

        super().__init__(**kwargs)

    @property
    def endpoint(self) -> SwaggerParser.Endpoint:
        return self._swagger_parser.get_endpoints()[self._name]

    @property
    def primary_key(self):
        if self.get_json_schema()["properties"].get("id"):
            return "id"
        return None

    def generate_looker_stream(self, name: str, request_params: Mapping[str, Any] = None) -> "LookerStream":
        return LookerStream(name,
                            authenticator=self.authenticator,
                            swagger_parser=self._swagger_parser,
                            domain=self._domain,
                            request_params=request_params)

    def get_parent_endpoints(self) -> List[SwaggerParser.Endpoint]:
        parts = self.endpoint.path.split("/")
        if len(parts) <= 3:
            return []

        parent_path = "/".join(parts[:-2])
        # self.logger.warning("%s => %s" % (parts, parent_path))
        for endpoint in self._swagger_parser.get_endpoints().values():
            if endpoint.path == parent_path:
                return [endpoint]

        # try to find a parent as the end of other path when a path has more then 1 parent
        # e.g. /dashboard_layouts/{dashboard_layout_id}/dashboard_layout_components"
        # => /dashboard_layouts => /dashboards/{dashboard_id}/dashboard_layouts
        for endpoint in self._swagger_parser.get_endpoints().values():
            if endpoint.path.endswith(parent_path):
                return [endpoint]
        raise LookerException(f"not found the parent endpoint: {parent_path}")

    @property
    def name(self):
        return self._name

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = self.endpoint.schema.get("items") or self.endpoint.schema
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": schema["properties"]
        }

    def path(self, stream_slice: Mapping[str, Any], **kwargs: Any) -> str:
        stream_slice = stream_slice or {}
        return self.endpoint.path.format(**stream_slice)[1:]

    def request_params(self, **kwargs: Any) -> MutableMapping[str, Any]:
        return self._request_params or None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        parent_endpoints = self.get_parent_endpoints()
        if not parent_endpoints:
            yield None
            return
        for parent_endpoint in parent_endpoints:
            parent_stream = self.generate_looker_stream(parent_endpoint.name)
            parent_key = self.slice_key or parent_endpoint.name[:-1] + "_id"
            for slice in parent_stream.stream_slices(sync_mode=sync_mode):
                for item in parent_stream.read_records(sync_mode=sync_mode, stream_slice=slice):
                    if item[self.parent_slice_key]:
                        yield {parent_key: item[self.parent_slice_key]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if isinstance(data, list):
            yield from data
        else:
            yield data


class ContentMetadata(LookerStream):
    parent_slice_key = "content_metadata_id"
    slice_key = "content_metadata_id"

    def get_parent_endpoints(self) -> List[SwaggerParser.Endpoint]:
        parent_names = ("dashboards", "folders", "homepages", "looks", "spaces")
        return [endpoint for name, endpoint in self._swagger_parser.get_endpoints().items() if name in parent_names]


class QueryHistory(BaseLookerStream):
    http_method = "POST"
    primary_key = ["query_id", "history_created_time"]
    cursor_field = "history_created_time"

    @property
    def state_checkpoint_interval(self):
        if self._is_finished:
            return 1
        return 100

    def path(self, **kwargs: Any):
        return "queries/run/json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._last_query_id = None
        self._is_finished = False

    def request_body_json(self, stream_state: MutableMapping[str, Any], **kwargs) -> Optional[Mapping]:
        latest_created_time = (stream_state or {}).get(self.cursor_field)

        if not latest_created_time:
            latest_created_time = "1970-01-01T00:00:00Z"

        dt = pendulum.parse(latest_created_time)
        dt_func = f"date_time({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute}, {dt.second})"
        # add column_limit as marker of connector query. All history items with this value will be skipped
        # its value shouldn't be changed in the future
        column_limit = 1205067
        return {
            "model": "i__looker",
            "view": "history",
            "limit": "10000",
            "column_limit": f"{column_limit}",

            "fields": [
                "query.id",

                "history.created_date",
                "history.created_time",

                "query.model",
                "query.view",
                "query.client_id",
                "query.column_limit",
                "space.id",
                "look.id",
                "dashboard.id",
                "user.id",
                "history.query_run_count",
                "history.total_runtime",
            ],
            "filters": {
                "query.model": "-EMPTY",
                "history.runtime": "NOT NULL",
                "user.is_looker": "No",

            },
            "filter_expression": f'${{history.created_time}} > {dt_func} AND (${{query.column_limit}} != {column_limit} OR is_null(${{query.column_limit}}))',
            "sorts": [
                "history.created_time", "query.id",
            ],
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        for i in range(len(records)):
            record = records[i]
            # self.logger.warning(str(record))
            if record.get("looker_error"):
                raise LookerException(f"Locker Error: {record['looker_error']}")
            # query.column_limit is used for filtering only
            record.pop("query.column_limit")
            # convert date to ISO format: 2021-10-12 10:46 => 2021-10-12T10:46:00Z
            record[self.cursor_field] = record.pop("history.created_time").replace(" ", "T") + "Z"

            if i >= len(records) - 1:
                self._is_finished = True
            # convert history.created_date => history_created_date etc
            yield {k.replace(".", "_"): v for k, v in record.items()}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        record_query_id = latest_record["query_id"]
        if not self._is_finished and self._last_query_id == record_query_id:
            if not self._last_query_id:
                self._last_query_id = record_query_id
            return current_stream_state
        return {
            self.cursor_field: max(
                (current_stream_state or {}).get(self.cursor_field) or "",
                latest_record[self.cursor_field]
            )
        }


class RunLooks(LookerStream):
    primary_key = None

    def __init__(self, run_look_ids: List[str], **kwargs: Any):
        self._run_look_ids = run_look_ids
        super().__init__(name="run_looks", **kwargs)

    @staticmethod
    def _get_run_look_key(look: Mapping[str, Any]):
        return f"{look['id']} - {look['title']}"

    def path(self, stream_slice: Mapping[str, Any], **kwargs: Any) -> str:
        return f'looks/{stream_slice["id"]}/run/json'

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        parent_stream = self.generate_looker_stream("search_looks",
                                                    request_params={
                                                        "id": ",".join(self._run_look_ids),
                                                        "limit": "10000",
                                                        "fields": "id,title,model(id)"
                                                    })
        found_look_ids = []
        for slice in parent_stream.stream_slices(sync_mode=sync_mode):
            for item in parent_stream.read_records(sync_mode=sync_mode, stream_slice=slice):
                if isinstance(item["model"], dict):
                    item["model"] = item.pop("model")["id"]
                found_look_ids.append(item["id"])
                yield item
        diff_ids = set(self._run_look_ids) - set(str(id) for id in found_look_ids)
        if diff_ids:
            raise LookerException(f"not found run_look_ids: {diff_ids}")

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response=response, stream_slice=stream_slice, **kwargs):
            yield {self._get_run_look_key(stream_slice): {k.replace(".", "_"): v for k, v in record.items()}}

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        For a given LookML model and field, looks up its type and generates
        its properties for the run_look endpoint JSON Schema
        """
        properties = {}
        for look_info in self.stream_slices(sync_mode=None):
            look_properties = {}
            for explore, fields in self._get_look_fields(look_info["id"]).items():
                explore_fields = self._get_explore_field_types(look_info["model"], explore)
                look_properties.update({field.replace(".", "_"): explore_fields[field] for field in fields})
            properties[self._get_run_look_key(look_info)] = {
                "title": look_info["title"],
                "properties": look_properties,
                "type": ["null", "object"],
                "additionalProperties": False,
            }
        # raise LookerException(properties)
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": properties,
        }

    def _get_look_fields(self, look_id) -> Mapping[str, List[str]]:
        stream = self.generate_looker_stream("look_info", request_params={
            "fields": "query(fields)"
        })
        slice = {"look_id": look_id}
        for item in stream.read_records(sync_mode=None, stream_slice=slice):
            explores = defaultdict(list)
            for field in item["query"]["fields"]:
                explores[field.split(".")[0]].append(field)
            return explores

        raise LookerException(f"not found fields for the look ID: {look_id}")

    def _get_explore_field_types(self, model: str, explore: str) -> Mapping[str, Any]:
        """
        For a given LookML model and explore, looks up its dimensions/measures
        and their types for run_look endpoint JSON Schema generation
        """
        stream = self.generate_looker_stream("explore_models", request_params={
            "fields": "fields(dimensions(name, type),measures(name, type))"
        })
        slice = {
            "lookml_model_name": model,
            "explore_name": explore
        }
        data = next(stream.read_records(sync_mode=None, stream_slice=slice))["fields"]
        fields = {}
        for dimension in data["dimensions"]:
            fields[dimension["name"]] = FIELD_TYPE_MAPPING.get(dimension["type"]) or "string"
        for measure in data["measures"]:
            fields[measure["name"]] = FIELD_TYPE_MAPPING.get(measure["type"]) or "number"
        for field_name in fields:
            schema = {}
            if "date" in fields[field_name]:
                schema = {"type": ["null", "string"], "format": fields[field_name]}
            else:
                schema = {"type": ["null", fields[field_name]]}
            fields[field_name] = schema
        return fields


class Dashboards(LookerStream):
    """Customization for dashboards stream because for 2 diff stream there is single endpoint only"""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response=response, **kwargs):
            # "id" of "dashboards" is integer
            # "id" of "lookml_dashboards" is string
            if self._name == "dashboards" and isinstance(record["id"], int):
                yield record
            elif self._name == "lookml_dashboards" and isinstance(record["id"], str):
                yield record
