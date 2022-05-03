#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type
from firebolt.client import DEFAULT_API_URL


def parse_config(config: json, logger: AirbyteLogger) -> Dict[str, Any]:
    """
    Convert dict of config values to firebolt.db.Connection arguments

    :param config: json-compatible dict of settings
    :param logger: AirbyteLogger instance to print logs.

    :return: dictionary of firebolt.db.Connection-compatible kwargs
    """
    connection_args = {
        "database": config["database"],
        "username": config["username"],
        "password": config["password"],
        "api_endpoint": config.get("host", DEFAULT_API_URL),
        "account_name": config.get("account"),
    }
    # engine can be a name or a full URL of a cluster
    engine = config.get("engine")
    if engine:
        if "." in engine:
            connection_args["engine_url"] = engine
        else:
            connection_args["engine_name"] = engine
    else:
        logger.info("Engine parameter was not provided. Connecting to the default engine.")
    return connection_args


def convert_type(fb_type: str, nullable: bool) -> Dict[str, Union[str, Dict]]:
    """
    Convert from Firebolt type to Airbyte. If type is not defined in
    Firebolt then it will be set to string, as per Airbyte reccommendation.

    :param fb_type: Firebolt type.

    :return: Dict containing Airbyte type specification.
    """
    map = {
        "VARCHAR": {"type": "string"},
        "TEXT": {"type": "string"},
        "STRING": {"type": "string"},
        "INTEGER": {"type": "integer"},
        "INT": {"type": "integer"},
        "FLOAT": {"type": "number"},
        "DOUBLE": {"type": "number"},
        "DOUBLE PRECISION": {"type": "number"},
        # Firebolt bigint is max 8 byte so it fits in Airbyte's "integer"
        "BIGINT": {"type": "integer"},
        "LONG": {"type": "integer"},
        "DECIMAL": {"type": "string", "airbyte_type": "big_number"},
        "DATE": {"type": "string", "format": "date"},
        "TIMESTAMP": {
            "type": "string",
            "format": "datetime",
            "airbyte_type": "timestamp_without_timezone",
        },
        "DATETIME": {
            "type": "string",
            "format": "datetime",
            "airbyte_type": "timestamp_without_timezone",
        },
    }
    if fb_type.upper().startswith("ARRAY"):
        inner_type = fb_type[6:-1]  # Strip ARRAY()
        # Array can't be nullable, but items can
        airbyte_type = convert_type(inner_type, nullable=True)
        result = {"type": "array", "items": airbyte_type}
    else:
        result = map.get(fb_type.upper(), {"type": "string"})
        if nullable:
            result["type"] = ["null", result["type"]]
    return result


def format_fetch_result(data: List[Any]) -> List[List[Any]]:
    """
    Format data from a firebolt query to be compatible with Airbyte.
    Convert Firebolt timestamp string to Airbyte.
    Firebolt stores dates in YYYY-MM-DD HH:mm:SS format.
    Airbyte requires YYYY-MM-DDTHH:mm:SS.

    :param fb_timestamp: timestamp string in YYYY-MM-DD HH:mm:SS format.

    :return: Airbyte timestamp string in YYYY-MM-DDTHH:mm:SS format.
    """

    for idx, item in enumerate(data):
        if type(item) == datetime:
            data[idx] = item.isoformat()
        elif type(item) == date:
            data[idx] = str(item)
        elif type(item) == list:
            data[idx] = format_fetch_result(item)
        elif type(item) == Decimal:
            data[idx] = str(item)
    return data


def airbyte_message_from_data(raw_data: List[List], columns: List[str], table_name: str) -> Optional[AirbyteMessage]:
    """
    Wrap data into an AirbyteMessage.

    :param raw_data: Raw data row returned from a fetch query
    :param columns: List of column names
    :param table_name: Name of a table where data was fetched from

    :return: AirbyteMessage containing parsed data
    """
    raw_data = format_fetch_result(raw_data)
    data = dict(zip(columns, raw_data))
    # Remove empty values
    data = {k: v for k, v in data.items() if v is not None}
    if not data:
        return None
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=table_name,
            data=data,
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )
