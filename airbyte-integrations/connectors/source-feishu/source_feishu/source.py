#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .common import (
    BASE_URL,
    get_bittabel_info,
    get_date_time,
    get_dict_key_value,
    get_header,
    get_wiki_spaces_node,
    get_bitable_data,
    get_table_list,
    get_table_view_list,
)
from .streams import FeishuInstancesStream, FeishuBitableStream


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
            else:
                bit_obj =  get_bitable_data(config, app_token)

            stream_kwargs = {
                "config": config, 
                "app_token": app_token,
                "table_id":None,
                "view_id":None,
                "object_name": "table", 
                "object_type": "table"
            }

            streams.append(FeishuBitableStream(**stream_kwargs))
            stream_kwargs.update({"object_name":"member","object_type":"member"});
            streams.append(FeishuBitableStream(**stream_kwargs))
            stream_kwargs.update({"object_name":"role","object_type":"role"});
            streams.append(FeishuBitableStream(**stream_kwargs))
            stream_kwargs.update({"object_name":"dashboard","object_type":"dashboard"});
            streams.append(FeishuBitableStream(**stream_kwargs))


            table_list = get_table_list(config, app_token)
            for table_obj in table_list:
                table_id = table_obj.get("table_id")
                tabel_name = table_obj.get("name")

                stream_kwargs.update({"table_id": table_id, "object_name":"view_"+table_id,"object_type":"view"});
                streams.append(FeishuBitableStream(**stream_kwargs))

                view_list = get_table_view_list(config, app_token, table_obj.get("table_id"))
                for view_obj in view_list:
                    view_id = view_obj.get("view_id")
                    view_name = view_obj.get("view_name")

                    stream_kwargs.update({"table_id": table_id, "view_id":view_id, "object_name":f"record_{view_id}","object_type":"record"});
                    streams.append(FeishuBitableStream(**stream_kwargs))
                    stream_kwargs.update({"table_id": table_id, "view_id":view_id, "object_name":f"field_{view_id}","object_type":"field"});
                    streams.append(FeishuBitableStream(**stream_kwargs))

        return streams
