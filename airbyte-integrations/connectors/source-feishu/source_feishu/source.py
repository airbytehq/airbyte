#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from json import JSONDecodeError
import requests
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_feishu.constraints import REFERAL_SCHEMA, SCHEMA_HEADERS


BASE_URL = "https://open.feishu.cn"


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    url = BASE_URL + "/open-apis/auth/v3/tenant_access_token/internal"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"app_id": config.get("app_id"), "app_secret": config.get("app_secret")}
    resp = requests.post(url, headers=header, json=body)
    resp_json = resp.json()
    if resp_json.get("code") == 0:
        header["Authorization"] = "Bearer " + resp_json.get("tenant_access_token")

    return header


def get_instances_detail(config: Mapping[str,Any], instance_id):
    url = BASE_URL + f"/open-apis/approval/v4/instances/{instance_id}?user_id_type=user_id"

    header = get_header(config)

    resp = requests.get(url, headers=header)
    resp_json = resp.json()
    if resp_json.get("code") == 0:
        return resp_json.get("data")

    return None


def get_date_time (config: Mapping[str, Any]) -> Mapping[str, Any]:
        
    today = datetime.today()
    end_time = today.strftime("%Y-%m-%d %H:%M:%S")
    day_ago = today + relativedelta(days=-1 * 1)
    start_time = day_ago.strftime("%Y-%m-%d %H:%M:%S")

    if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
        days = config["tunnel_method"]["days"]
        today = datetime.today()
        day_ago = today + relativedelta(hours=-1 * days)
        start_time = day_ago.strftime("%Y-%m-%d %H:%M:%S")
        end_time = today.strftime("%Y-%m-%d %H:%M:%S")

    else:
        start_time = config["tunnel_method"]["start_time"]
        end_time = config["tunnel_method"]["end_time"]

    datetime_ob_s = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    obj_stamp_s = int(time.mktime(datetime_ob_s.timetuple()) * 1000.0 + datetime_ob_s.microsecond / 1000.0)
    datetime_obj_e = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    obj_stamp_e = int(time.mktime(datetime_obj_e.timetuple()) * 1000.0 + datetime_obj_e.microsecond / 1000.0)

    return {
        "start_time": obj_stamp_s,
        "end_time": obj_stamp_e
    }


class FeishuStream(HttpStream, ABC):
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
        schema = REFERAL_SCHEMA
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
            schema = REFERAL_SCHEMA
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
        print("self.page_token",self.page_token)
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
        print(response.url)
        print(response.text)

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


# Source
class SourceFeishu(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = get_header(config)

        object_types = config.get("object_types")
        approval_code = object_types[0]

        date_time_o = get_date_time(config)

        params = {
            "approval_code": approval_code, 
            "page_size": "100", 
            "start_time": date_time_o.get("start_time"), 
            "end_time": date_time_o.get("end_time"), 
            "page_token": ""
            }
        url = BASE_URL + "/open-apis/approval/v4/instances"

        resp = requests.get(url, headers=headers, params=params)

        resp_json = resp.json()
        if resp_json.get("code") == 0:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {resp.text}"

    # def get_session(self, auth: str) -> requests.Session:
    #     session = requests.Session()
    #     session.auth = auth
    #     return session

    def generate_stream(
        self,
        config: Mapping[str, Any],
        object_name: str,
    ) -> FeishuStream:
        input_args = {
        }
        return FeishuStream(config=config,object_name=object_name)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        object_names = config.get("object_types")

        # build streams
        streams: list = []
        for name in object_names:
            stream = self.generate_stream(config=config, object_name=name)
            if stream:
                streams.append(stream)
        return streams
