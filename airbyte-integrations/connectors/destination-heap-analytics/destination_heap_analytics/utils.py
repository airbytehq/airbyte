#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import datetime
from typing import Any, Dict, List, Mapping

import pendulum


def datetime_to_string(date: datetime.datetime) -> str:
    return date.to_iso8601_string()


def flatten_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    out = {}

    def flatten(x: Dict[str, Any], prefix=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], prefix + a + ".")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, prefix + str(i) + ".")
                i += 1
        else:
            out[prefix[:-1]] = x

    flatten(obj)
    return out


def parse_property_json(data: Dict[str, any], property_columns: List[str]) -> Mapping[str, Any]:
    if len(property_columns) == 1 and property_columns[0] == "*":
        return {**(data or {})}
    else:
        properties = {}
        for column in property_columns:
            if column in data and data[column] is not None:
                properties[column] = data[column]
        return properties


def parse_event_json(
    data: Dict[str, any], property_columns: List[str], event_column: str, identity_column: str, timestamp_column: str = None, **kwargs
) -> Mapping[str, Any]:
    timestamp = data.get(timestamp_column) if data.get(timestamp_column) else datetime_to_string(pendulum.now("UTC"))
    event = data.get(event_column)
    identity = data.get(identity_column)
    if timestamp and event and identity:
        properties = parse_property_json(data=data, property_columns=property_columns)
        return {
            "identity": identity,
            "event": event,
            "timestamp": timestamp,
            "properties": properties,
        }
    else:
        return None


def parse_aup_json(data: Dict[str, any], property_columns: List[str], identity_column: str, **kwargs) -> Mapping[str, Any]:
    identity = data.get(identity_column)
    if identity:
        properties = parse_property_json(data=data, property_columns=property_columns)
        return {
            "identity": identity,
            "properties": properties,
        }
    else:
        return None


def parse_aap_json(data: Dict[str, any], property_columns: List[str], account_id_column: str, **kwargs) -> Mapping[str, Any]:
    account_id = data.get(account_id_column)
    if account_id:
        properties = parse_property_json(data=data, property_columns=property_columns)
        return {
            "account_id": account_id,
            "properties": properties,
        }
    else:
        return None
