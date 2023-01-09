#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import functools
from abc import ABC
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from prance import ResolvingParser

API_VERSION = "3.1"

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
    """Base looker class"""

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def primary_key(self) -> Optional[Union[str, List[str]]]:
        return None

    def __init__(self, *, domain: str, **kwargs: Any):
        self._domain = domain
        super().__init__(**kwargs)

    @property
    def authenticator(self) -> TokenAuthenticator:
        if self._session.auth:
            return self._session.auth
        return super().authenticator

    @property
    def url_base(self) -> str:
        return f"https://{self._domain}/api/{API_VERSION}/"

    def next_page_token(self, response: requests.Response, **kwargs: Any) -> Optional[Mapping[str, Any]]:
        return None


class SwaggerParser(BaseLookerStream):
    """Convertor Swagger file to stream schemas
    https://<domain>/api/<api_version>/swagger.json
    """

    class Endpoint:
        def __init__(self, *, name: str, path: str, schema: Mapping[str, Any], operation_id: str, summary: str):
            self.name, self.path, self.schema, self.operation_id, self.summary = name, path, schema, operation_id, summary

    def path(self, **kwargs: Any) -> str:
        return "swagger.json"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs: Any) -> Iterable[Mapping]:
        yield ResolvingParser(spec_string=response.text)

    @functools.lru_cache(maxsize=None)
    def get_endpoints(self) -> Mapping[str, "Endpoint"]:
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
            endpoints[name] = self.Endpoint(
                name=name, path=path, schema=self.format_schema(schema), summary=get_data["summary"], operation_id=get_data["operationId"]
            )

        # stream "lookml_dashboards" uses same endpoints
        # "lookml_dashboards" and "dashboards" have one different only:
        # "id" of "dashboards" is integer
        # "id" of "lookml_dashboards" is string
        dashboards_schema = endpoints["dashboards"].schema
        lookml_dashboards_schema = copy.deepcopy(dashboards_schema)
        dashboards_schema["items"]["properties"]["id"]["type"] = "integer"
        lookml_dashboards_schema["items"]["properties"]["id"]["type"] = "string"
        endpoints["lookml_dashboards"] = self.Endpoint(
            name="lookml_dashboards",
            path=endpoints["dashboards"].path,
            schema=lookml_dashboards_schema,
            summary=endpoints["dashboards"].summary,
            operation_id=endpoints["dashboards"].operation_id,
        )
        return endpoints

    @classmethod
    def format_schema(cls, schema: Mapping[str, Any], key: str = None) -> Dict[str, Any]:
        """Clean and validates all swagger "response" schemas
        The Looker swagger file includes custom Locker fields (x-looker-...) and
        it doesn't support multi typing( ["null", "..."])
        """
        updated_schema: Dict[str, Any] = {}
        object_type: Union[str, List[str]] = schema.get("type")
        if "properties" in schema:
            object_type = ["null", "object"]
            updated_sub_schemas: Dict[str, Any] = {}
            for key, sub_schema in schema["properties"].items():
                updated_sub_schemas[key] = cls.format_schema(sub_schema, key=key)
            updated_schema["properties"] = updated_sub_schemas

        elif "items" in schema:
            object_type = ["null", "array"]
            updated_schema["items"] = cls.format_schema(schema["items"])

        if "format" in schema:
            if schema["format"] == "int64" and (not key or not key.endswith("id")):
                updated_schema["multipleOf"] = 10**-16
                object_type = "number"
            else:
                updated_schema["format"] = schema["format"]
        if "description" in schema:
            updated_schema["description"] = schema["description"]

        if schema.get("x-looker-nullable") is True and isinstance(object_type, str):
            object_type = ["null", object_type]
        updated_schema["type"] = object_type
        return updated_schema


class LookerStream(BaseLookerStream, ABC):
    # keys for correct mapping between parent and current streams.
    # Several streams have some special aspects
    parent_slice_key = "id"
    custom_slice_key: str = None

    def __init__(self, name: str, swagger_parser: SwaggerParser, request_params: Mapping[str, Any] = None, **kwargs: Any):
        self._swagger_parser = swagger_parser
        self._name = name
        self._request_params = request_params
        super().__init__(**kwargs)

    @property
    def endpoint(self) -> SwaggerParser.Endpoint:
        """Extracts endpoint options"""
        return self._swagger_parser.get_endpoints()[self._name]

    @property
    def primary_key(self) -> Optional[Union[str, List[str]]]:
        """not all streams have primary key"""
        if self.get_json_schema()["properties"].get("id"):
            return "id"
        return None

    def generate_looker_stream(self, name: str, request_params: Mapping[str, Any] = None) -> "LookerStream":
        """Generate a stream object. It can be used for loading of parent data"""
        return LookerStream(
            name, authenticator=self.authenticator, swagger_parser=self._swagger_parser, domain=self._domain, request_params=request_params
        )

    def get_parent_endpoints(self) -> List[SwaggerParser.Endpoint]:
        parts = self.endpoint.path.split("/")
        if len(parts) <= 3:
            return []

        parent_path = "/".join(parts[:-2])
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
    def name(self) -> str:
        return self._name

    @classmethod
    def format_null_in_schema(cls, schema: Mapping[str, Any]):
        """Add 'null' to schema type field

        Output:
            {
            ...
            'type': ['null', 'object']
            'properties':   {
                'field':{
                    'type': ['null', 'number']
                        }
                }
            ...
            }

        """

        for key, value_schema in schema.items():
            if isinstance(value_schema, dict):
                schema_type = value_schema.get("type")

                if isinstance(schema_type, str):
                    value_schema["type"] = ["null", schema_type]

                schema[key] = cls.format_null_in_schema(value_schema)

        return schema

    def get_json_schema(self) -> Mapping[str, Any]:
        # Overrides default logic. All schema should be generated dynamically.
        schema = self.endpoint.schema.get("items") or self.endpoint.schema
        schema = self.format_null_in_schema(schema["properties"])
        return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": schema}

    def path(self, stream_slice: Mapping[str, Any], **kwargs: Any) -> str:
        stream_slice = stream_slice or {}
        return self.endpoint.path.format(**stream_slice)[1:]

    def request_params(self, **kwargs: Any) -> Optional[Mapping[str, Any]]:
        return self._request_params or None

    def stream_slices(self, sync_mode: SyncMode, **kwargs: Any) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_endpoints = self.get_parent_endpoints()
        if not parent_endpoints:
            yield None
            return
        for parent_endpoint in parent_endpoints:
            parent_stream = self.generate_looker_stream(parent_endpoint.name)

            # if self.custom_slice_key is None, this logic will generate it itself with the following rule:
            # parent_name has the 's' at the end and its template key has "_id" at the end
            # e.g. dashboards => dashboard_id
            parent_key = self.custom_slice_key or parent_endpoint.name[:-1] + "_id"
            for slice in parent_stream.stream_slices(sync_mode=sync_mode):
                for item in parent_stream.read_records(sync_mode=sync_mode, stream_slice=slice):
                    if item[self.parent_slice_key]:
                        yield {parent_key: item[self.parent_slice_key]}

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs: Any) -> Iterable[Mapping]:
        """Parses data. The Looker API doesn't support pagination logis.
        Thus all responses are or JSON list or target single object.
        """
        data = response.json()
        if isinstance(data, list):
            yield from data
        else:
            yield data


class ContentMetadata(LookerStream):
    """ContentMetadata stream has personal customization. Because it has several parent streams"""

    parent_slice_key = "content_metadata_id"
    custom_slice_key = "content_metadata_id"

    def get_parent_endpoints(self) -> List[SwaggerParser.Endpoint]:
        parent_names = ("dashboards", "folders", "homepages", "looks", "spaces")
        return [endpoint for name, endpoint in self._swagger_parser.get_endpoints().items() if name in parent_names]


class QueryHistory(BaseLookerStream):
    """This stream is custom Looker query. That its response has a individual static schema."""

    http_method = "POST"
    cursor_field = "history_created_time"
    # all connector's request should have this value of as prefix of queries' client_id
    airbyte_client_id_prefix = "AiRbYtE2"

    @property
    def primary_key(self) -> Optional[Union[str, List[str]]]:
        return ["query_id", "history_created_time"]

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """this is a workaround: the Airbyte CDK forces for save the latest state after reading of all records"""
        if self._is_finished:
            return 1
        return 100

    def path(self, **kwargs: Any) -> str:
        return "queries/run/json"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._last_query_id = None
        self._is_finished = False

    def get_query_client_id(self, stream_state: MutableMapping[str, Any]) -> str:
        """
         The query client_id is used for filtering because this query metadata is added to a response of this request
        and the connector should skip our request information.
         Values of the client_id is unique for every request body. it must be changed if any query symbol is changed.
        But for incremental logic we have to add dynamic filter conditions. The single query's updating is stream_state value
        thus it can be used as a part of client_id values. e.g.:
            stream_state 2050-01-01T00:00:00Z -> client_id AiRbYtE225246479800000
        """
        latest_created_time = (stream_state or {}).get(self.cursor_field)
        timestamp = 0
        if latest_created_time:
            dt = pendulum.parse(latest_created_time)  # type: ignore[attr-defined]
            timestamp = int(dt.timestamp())
        # client_id has the hard-set length (22 symbols) this we add "0" to the end
        return f"{self.airbyte_client_id_prefix}{timestamp}".ljust(22, "0")

    def request_body_json(self, stream_state: MutableMapping[str, Any], **kwargs: Any) -> Optional[Mapping]:
        latest_created_time = (stream_state or {}).get(self.cursor_field)

        if not latest_created_time:
            latest_created_time = "1970-01-01T00:00:00Z"

        dt = pendulum.parse(latest_created_time)  # type: ignore[attr-defined]
        dt_func = f"date_time({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute}, {dt.second})"
        client_id = self.get_query_client_id(stream_state)

        # need to add the custom client_id value. It is used for filtering
        # its value shouldn't be changed in the future
        return {
            "model": "i__looker",
            "view": "history",
            "limit": "10000",
            "client_id": client_id,
            "fields": [
                "query.id",
                "history.created_date",
                "history.created_time",
                "query.client_id",
                "query.model",
                "query.view",
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
            "filter_expression": f"${{history.created_time}} > {dt_func}",
            "sorts": [
                "history.created_time",
                "query.id",
            ],
        }

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs: Any) -> Iterable[Mapping]:
        records = response.json()
        for i in range(len(records)):
            record = records[i]
            if record.get("looker_error"):
                raise LookerException(f"Locker Error: {record['looker_error']}")
            if (record.get("query.client_id") or "").startswith(self.airbyte_client_id_prefix):
                # skip all native connector's requests
                continue
            # query.column_limit is used for filtering only
            record.pop("query.client_id", None)

            # convert date to ISO format: 2021-10-12 10:46 => 2021-10-12T10:46:00Z
            record[self.cursor_field] = record.pop("history.created_time").replace(" ", "T") + "Z"

            if i >= len(records) - 1:
                self._is_finished = True
            # convert history.created_date => history_created_date etc
            yield {k.replace(".", "_"): v for k, v in record.items()}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        record_query_id = latest_record["query_id"]
        if not self._is_finished and self._last_query_id == record_query_id:
            if not self._last_query_id:
                self._last_query_id = record_query_id
            return current_stream_state
        return {self.cursor_field: max((current_stream_state or {}).get(self.cursor_field) or "", latest_record[self.cursor_field])}


class RunLooks(LookerStream):
    """ "
    Runs ready looks' requests
    Docs: https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/look#run_look
    """

    @property
    def primary_key(self) -> Optional[Union[str, List[str]]]:
        return None

    def __init__(self, run_look_ids: List[str], **kwargs: Any):
        self._run_look_ids = run_look_ids
        super().__init__(name="run_looks", **kwargs)

    @staticmethod
    def _get_run_look_key(look: Mapping[str, Any]) -> str:
        return f"{look['id']} - {look['title']}"

    def path(self, stream_slice: Mapping[str, Any], **kwargs: Any) -> str:
        return f'looks/{stream_slice["id"]}/run/json'

    def stream_slices(self, sync_mode: SyncMode, **kwargs: Any) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream = self.generate_looker_stream(
            "search_looks", request_params={"id": ",".join(self._run_look_ids), "limit": "10000", "fields": "id,title,model(id)"}
        )
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

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs: Any) -> Iterable[Mapping]:
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
                "additionalProperties": True,
            }
        # raise LookerException(properties)
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": properties,
        }

    def _get_look_fields(self, look_id: int) -> Mapping[str, List[str]]:
        stream = self.generate_looker_stream("look_info", request_params={"fields": "query(fields)"})
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
        stream = self.generate_looker_stream(
            "explore_models", request_params={"fields": "fields(dimensions(name, type),measures(name, type))"}
        )
        slice = {"lookml_model_name": model, "explore_name": explore}
        data = next(stream.read_records(sync_mode=None, stream_slice=slice))["fields"]
        fields = {}
        for dimension in data["dimensions"]:
            fields[dimension["name"]] = FIELD_TYPE_MAPPING.get(dimension["type"]) or "string"
        for measure in data["measures"]:
            fields[measure["name"]] = FIELD_TYPE_MAPPING.get(measure["type"]) or "number"
        field_types = {}
        for field_name in fields:
            if "date" in fields[field_name]:
                schema = {"type": ["null", "string"], "format": fields[field_name]}
            else:
                schema = {"type": ["null", fields[field_name]]}
            field_types[field_name] = schema
        return field_types


class Dashboards(LookerStream):
    """Customization for dashboards stream because for 2 diff stream there is single endpoint only"""

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs: Any) -> Iterable[Mapping]:
        for record in super().parse_response(response=response, stream_slice=stream_slice, **kwargs):
            # "id" of "dashboards" is integer
            # "id" of "lookml_dashboards" is string
            if self._name == "dashboards" and isinstance(record["id"], int):
                yield record
            elif self._name == "lookml_dashboards" and isinstance(record["id"], str):
                yield record
