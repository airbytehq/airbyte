#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
import time
from abc import ABC
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from dateutil.relativedelta import relativedelta

BASE_URL = "https://open.feishu.cn"


def get_dict_key_value(config: Mapping[str, Any], key: str):
    ret_value = None
    if config.__contains__(key):
        ret_value = config.get(key)
    return ret_value


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


def get_instances_detail(config: Mapping[str, Any], instance_id):
    url = BASE_URL + f"/open-apis/approval/v4/instances/{instance_id}?user_id_type=user_id"

    header = get_header(config)

    resp = requests.get(url, headers=header)
    resp_json = resp.json()
    if resp_json.get("code") == 0:
        return resp_json.get("data")

    return None


def get_date_time(config: Mapping[str, Any]) -> Mapping[str, Any]:
    today = datetime.today()
    end_time = today.strftime("%Y-%m-%d %H:%M:%S")
    day_ago = today + relativedelta(days=-1 * 1)
    start_time = day_ago.strftime("%Y-%m-%d %H:%M:%S")

    if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
        days = config["tunnel_method"]["days"]
        today = datetime.today()
        day_ago = today + relativedelta(days=-1 * days)
        start_time = day_ago.strftime("%Y-%m-%d %H:%M:%S")
        end_time = today.strftime("%Y-%m-%d %H:%M:%S")

    else:
        start_time = config["tunnel_method"]["start_time"]
        end_time = config["tunnel_method"]["end_time"]

    datetime_ob_s = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    obj_stamp_s = int(time.mktime(datetime_ob_s.timetuple()) * 1000.0 + datetime_ob_s.microsecond / 1000.0)
    datetime_obj_e = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    obj_stamp_e = int(time.mktime(datetime_obj_e.timetuple()) * 1000.0 + datetime_obj_e.microsecond / 1000.0)

    return {"start_time": obj_stamp_s, "end_time": obj_stamp_e}


# 解析URL地址，获取 app_token, table_id, view_id
def get_bittabel_info(str):
    wiki_arr = re.findall(r"/wiki/", str)

    ar = []
    if len(wiki_arr) > 0:
        ar = re.findall(r"/wiki/(\w+)\?table=(\w+)\&view=(\w+)", str, re.S)
    else:
        ar = re.findall(r"/base/(\w+)\?table=(\w+)\&view=(\w+)", str, re.S)

    bit_table_info = {}
    if len(ar) > 0:
        if len(ar[0]) == 3:
            bit_table_info = {"app_token": ar[0][0], "table_id": ar[0][1], "view_id": ar[0][2]}
    return bit_table_info


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    url = BASE_URL + "/open-apis/auth/v3/tenant_access_token/internal"
    header = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json; charset=utf-8"}

    header = {}
    body = {"app_id": config.get("app_id"), "app_secret": config.get("app_secret")}
    resp = requests.post(url, headers=header, json=body)
    resp_json = resp.json()
    if resp_json.get("code") == 0:
        header["Authorization"] = "Bearer " + resp_json.get("tenant_access_token")

    return header


def get_wiki_spaces_node(config: Mapping[str, Any], node_token: str):
    url = BASE_URL + f"/open-apis/wiki/v2/spaces/get_node?token={node_token}"

    header = get_header(config)

    resp = requests.get(url, headers=header)
    resp_json = resp.json()

    if resp_json.get("code") == 0:
        return resp_json.get("data").get("node")
    return None


def get_table_field(name, type):
    table_field = {
        "record_list": {"table": True, "view": True},
        "field_list": {"table": True, "view": False},
        "view_list": {"table": True, "view": True},
        "table_list": {"table": True, "view": False},
        "member_list": {"table": False, "view": False},
        "role_list": {"table": False, "view": False},
        "dashboard_list": {"table": False, "view": False},
    }

    flag = table_field.get(name, False)
    if flag == False:
        return False
    return flag.get(type, False)


def get_result_node(name):
    result_node = {
        "record_list": "items",
        "field_list": "items",
        "view_list": "items",
        "table_list": "items",
        "member_list": "items",
        "role_list": "items",
        "dashboard_list": "dashboards",
    }

    return result_node.get(name, False)
