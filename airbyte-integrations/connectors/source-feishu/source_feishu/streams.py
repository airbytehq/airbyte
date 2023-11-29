#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from json import JSONDecodeError
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream

from .common import BASE_URL, get_date_time, get_header, get_instances_detail, get_table_field, get_result_node
from .constraints import INSTANCES_SCHEMA, VIEW_LIST_SCHEMA, TABLE_LIST_SCHEMA, ROLE_LIST_SCHEMA, RECORD_LIST_SCHEMA, MEMBER_LIST_SCHEMA, FIELD_LIST_SCHEMA, DASHBOARD_LIST_SCHEMA


class FeishuInstancesStream(HttpStream, ABC):
    primary_key = None

    def __init__(self, config: Mapping[str, Any], object_name, **kwargs):
        super().__init__(**kwargs)
        self.config_param = config
        self.page_size = 100
        self.page_token = None
        self.approval_code = object_name
        self.start_time = None
        self.end_time = None
        self.object_name = object_name
        self.schemas = {}  # store subschemas to reduce API calls

    @property
    def http_method(self) -> str:
        return "GET"

    @property
    def name(self) -> str:
        return self.object_name

    @property
    def url_base(self) -> str:
        return BASE_URL

    @property
    def ref_schema(self) -> Mapping[str, str]:
        schema = INSTANCES_SCHEMA
        return schema

    def get_schema(self, ref: str) -> Union[Mapping[str, Any], str]:
        def get_json_response(response: requests.Response) -> dict:
            try:
                return response.json()
            except JSONDecodeError as e:
                self.logger.error(f"Cannot get schema for {self.name}, actual response: {e.response.text}")
                raise

        # try to retrieve the schema from the cache
        schema = self.schemas.get(ref)
        if not schema:
            schema = INSTANCES_SCHEMA
            self.schemas[ref] = schema
        return schema

    def build_schema(self, record: Any) -> Mapping[str, Any]:
        # recursively build a schema with subschemas
        if isinstance(record, dict):
            # Netsuite schemas do not specify if fields can be null, or not
            # as Airbyte expects, so we have to allow every field to be null
            property_type = record.get("type")
            property_type_list = property_type if isinstance(property_type, list) else [property_type]
            # ensure there is a type, type is the json schema type and not a property
            # and null has not already been added
            if property_type and not isinstance(property_type, dict) and "null" not in property_type_list:
                record["type"] = ["null"] + property_type_list
            # removing non-functional elements from schema

            return {k: self.build_schema(v) for k, v in record.items()}
        else:
            return record

    def get_json_schema(self, **kwargs) -> dict:
        schema = self.get_schema(self.name)
        return self.build_schema(schema)

    def path(self, **kwargs) -> str:
        return "/open-apis/approval/v4/instances"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        respJson = response.json()
        page_token = respJson.get("data").get("page_token")
        if page_token:
            self.page_token = page_token
            return {"page_token": self.page_token}

        self.page_token = None
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        dt_dict = get_date_time(config=self.config_param)

        return {
            "page_size": self.page_size,
            "page_token": self.page_token,
            "approval_code": self.approval_code,
            "start_time": dt_dict.get("start_time"),
            "end_time": dt_dict.get("end_time"),
        }

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respJson = response.json()

        if respJson.get("code") == 0:
            page_token = respJson.get("data").get("page_token")
            if page_token is not None:
                self.page_token = page_token
            results = respJson.get("data").get("instance_code_list")
            ret_list = []
            if results is None:
                return []
            for item in results:
                detail = get_instances_detail(self.config_param, item)
                ret_list.append(detail)
            return ret_list
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])


# Basic full refresh stream
class FeishuBitableStream(HttpStream, ABC):

    primary_key = None

    def __init__(self, config: Mapping[str, Any], app_token, table_id, view_id, object_name, object_type, **kwargs):
        super().__init__(**kwargs)

        self.config_param = config
        self.page_size = 10
        self.page_token = None
        self.app_token = app_token
        self.table_id = table_id
        self.view_id = view_id
        self.object_name = object_name
        self.object_type = object_type
        self.current_page = None

    @property
    def http_method(self) -> str:
        return "GET"

    @property
    def url_base(self) -> str:
        return BASE_URL

    def path(self, **kwargs) -> str:

        if "record"== self.object_type:
            return f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        elif "member" == self.object_type:
            return f"/open-apis/drive/v1/permissions/{self.app_token}/members"
        elif "field" == self.object_type:
            return f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/fields"
        elif "view" == self.object_type:
            return f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/views"
        elif "table" == self.object_type:
            return f"/open-apis/bitable/v1/apps/{self.app_token}/tables"
        elif "role" == self.object_type:
            return f"/open-apis/bitable/v1/apps/{self.app_token}/roles"
        
        return f"/open-apis/bitable/v1/apps/{self.app_token}/dashboards"
    
    @property
    def name(self) -> str:
        return self.object_name
    
    @property
    def ref_schema(self) -> Mapping[str, str]:

        if "view"== self.object_type:
            return  VIEW_LIST_SCHEMA
        elif "table" == self.object_type:
            return  TABLE_LIST_SCHEMA
        elif "role" == self.object_type:
            return ROLE_LIST_SCHEMA
        elif "record" == self.object_type:
            return  RECORD_LIST_SCHEMA
        elif "member" == self.object_type:
            return   MEMBER_LIST_SCHEMA
        elif "field" == self.object_type:
            return   FIELD_LIST_SCHEMA
        elif "dashboard" == self.object_type:
            return  DASHBOARD_LIST_SCHEMA

    def get_schema(self, ref: str) -> Union[Mapping[str, Any], str]:

        if "view"== self.object_type:
            return  VIEW_LIST_SCHEMA
        elif "table" == self.object_type:
            return  TABLE_LIST_SCHEMA
        elif "role" == self.object_type:
            return ROLE_LIST_SCHEMA
        elif "record" == self.object_type:
            return  RECORD_LIST_SCHEMA
        elif "member" == self.object_type:
            return   MEMBER_LIST_SCHEMA
        elif "field" == self.object_type:
            return   FIELD_LIST_SCHEMA
        elif "dashboard" == self.object_type:
            return  DASHBOARD_LIST_SCHEMA

    def build_schema(self, record: Any) -> Mapping[str, Any]:
        # recursively build a schema with subschemas
        if isinstance(record, dict):
            # Netsuite schemas do not specify if fields can be null, or not
            # as Airbyte expects, so we have to allow every field to be null
            property_type = record.get("type")

            property_type_list = property_type if isinstance(property_type, list) else [property_type]
            # ensure there is a type, type is the json schema type and not a property
            # and null has not already been added
            if property_type and not isinstance(property_type, dict) and "null" not in property_type_list:
                record["type"] = ["null"] + property_type_list
            # removing non-functional elements from schema

            return {k: self.build_schema(v) for k, v in record.items()}
        else:
            return record

    def get_json_schema(self, **kwargs) -> dict:
        schema = self.get_schema(self.name)
        return self.build_schema(schema)


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        respJson = response.json()
        page_token = respJson.get("data").get("page_token")
        has_more = respJson.get("data").get("has_more")
        if has_more is not None:
            if has_more:
                self.page_token = page_token
                return None
            else:
                self.page_token = None
                return None
        if page_token:
            self.page_token = page_token
            return {"page_token": self.page_token}

        self.page_token = None
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if "record" == self.object_type:
            return {"page_size": "500", "page_token": self.page_token, "view_id": self.view_id}
        elif "member" == self.object_type:
            return {"type": "bitable"}
        elif "role" == self.object_type:
            return {"page_size": "30", "page_token": self.page_token}
        return {"page_size": self.page_size, "page_token": self.page_token}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respJson = response.json()
        if respJson.get("code") == 0:
            page_token = respJson.get("data").get("page_token")
            if page_token is not None:
                self.page_token = page_token

            node_name = get_result_node(self.object_type)
            results = respJson.get("data").get(node_name)

            ret_list = []
            if results is None:
                return []
            for item in results:
                if item.get("app_token") is None:
                    item["app_token"] = self.app_token
                if get_table_field(self.object_type, "table"):
                    if item.get("table_id") is None:
                        item["table_id"] = self.table_id
                if get_table_field(self.object_type, "view"):
                    if item.get("view_id") is None:
                        item["view_id"] = self.view_id
                if get_table_field(self.object_type, "field"):
                    print(item)
                    if item.get("table_id") is None:
                        item["table_id"] = self.table_id
                    if item.get("view_id") is None:
                        item["view_id"] = self.view_id
                ret_list.append(item)
            return ret_list

        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": respJson}])
