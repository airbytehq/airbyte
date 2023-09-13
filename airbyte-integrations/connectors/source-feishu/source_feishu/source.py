#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .common import BASE_URL, get_bittabel_info, get_date_time, get_dict_key_value, get_header, get_wiki_spaces_node
from .constraints import REFERAL_SCHEMA, SCHEMA_HEADERS
from .streams import DashboardList, FeishuInstancesStream, FieldList, MemberList, RecordList, RoleList, TableList, ViewList


# Source
class SourceFeishu(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = get_header(config)

        resp_list = []

        flag = False
        object_types = get_dict_key_value(config=config, key="object_types")
        if object_types is not None:
            flag = True
            for obj in object_types:
                date_time_o = get_date_time(config)

                params = {
                    "approval_code": obj,
                    "page_size": "100",
                    "start_time": date_time_o.get("start_time"),
                    "end_time": date_time_o.get("end_time"),
                    "page_token": "",
                }
                url = BASE_URL + "/open-apis/approval/v4/instances"

                resp = requests.get(url, headers=headers, params=params)

                resp_json = resp.json()
                if resp_json.get("code") != 0:
                    resp_list.append(obj)

        bit_table_link = get_dict_key_value(config=config, key="bit_table_link")
        if bit_table_link is not None:
            flag = True
            bittable_info = get_bittabel_info(bit_table_link)
            app_token = bittable_info["app_token"]
            if bit_table_link.find("/wiki/") > -1:
                node_obj = get_wiki_spaces_node(config, app_token)
                app_token = node_obj.get("obj_token")
            if len(bittable_info) == 3:
                url = f"{BASE_URL}/open-apis/bitable/v1/apps/{app_token}"
                resp = requests.get(url, headers=headers)
                resp_json = resp.json()
                if resp_json.get("code") != 0:
                    resp_list.append(bit_table_link)
            else:
                resp_list.append(bit_table_link)

        if flag == False:
            return False, "No streams to connect to from source, Please check Approval Code or bittable link"

        if len(resp_list) == 0:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {','.join(resp_list)}"

    def generate_stream(
        self,
        config: Mapping[str, Any],
        object_name: str,
    ) -> FeishuInstancesStream:
        input_args = {}
        return FeishuInstancesStream(config=config, object_name=object_name)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        object_names = get_dict_key_value(config=config, key="object_types")

        bit_table_link = get_dict_key_value(config=config, key="bit_table_link")

        # build streams
        streams: list = []

        if object_names is not None:
            for name in object_names:
                stream = self.generate_stream(config=config, object_name=name)
                if stream:
                    streams.append(stream)

        if bit_table_link is not None:
            bittable_info = get_bittabel_info(bit_table_link)
            app_token = bittable_info["app_token"]
            table_id = bittable_info["table_id"]
            view_id = bittable_info["view_id"]
            if bit_table_link.find("/wiki/") > -1:
                node_obj = get_wiki_spaces_node(config, app_token)
                app_token = node_obj.get("obj_token")

            stream_kwargs = {"config": config, "app_token": app_token, "table_id": table_id, "view_id": view_id}

            streams.append(RecordList(**stream_kwargs))
            streams.append(FieldList(**stream_kwargs))
            streams.append(ViewList(**stream_kwargs))
            streams.append(TableList(**stream_kwargs))
            streams.append(MemberList(**stream_kwargs))
            streams.append(RoleList(**stream_kwargs))
            streams.append(DashboardList(**stream_kwargs))

        return streams
