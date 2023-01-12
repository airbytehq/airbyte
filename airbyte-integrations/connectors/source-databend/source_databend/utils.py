#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type


def convert_type(databend_type: str, nullable: bool) -> Dict[str, Union[str, Dict]]:
    """
    Convert from Databend type to Airbyte. If type is not defined in
    Databend then it will be set to string, as per Airbyte reccommendation.
    More on Databend types can be found in docs:
    https://databend.rs/doc/sql-reference/data-types/

    :param databend_type: Databend type.

    :return: Dict containing Airbyte type specification.
    """
    map = {
        "VARCHAR": {"type": "string"},
        "TINYINT": {"type": "integer"},
        "SMALLINT": {"type": "integer"},
        "INT": {"type": "integer"},
        "BIGINT": {"type": "integer"},
        "FLOAT": {"type": "number"},
        "DOUBLE": {"type": "number"},
        "BOOLEAN": {"type": "integer"},
        "ARRAY": {"type": "string"},
        "OBJECT": {"type": "string"},
        "VARIANT": {"type": "string"},
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
    if databend_type.upper().startswith("ARRAY"):
        inner_type = databend_type[6:-1]  # Strip ARRAY()
        # Array can't be nullable, but items can
        airbyte_type = convert_type(inner_type, nullable=True)
        result = {"type": "array", "items": airbyte_type}
    else:
        # Remove NULL/NOT NULL from child type of an array e.g. ARRAY(INT NOT NULL)
        databend_type = databend_type.removesuffix(" NOT NULL").removesuffix(" NULL")
        result = map.get(databend_type.upper(), {"type": "string"})
        if nullable:
            result["type"] = ["null", result["type"]]
    return result


def format_fetch_result(data: List[Any]) -> List[List[Any]]:
    """
    Format data from a Databend query to be compatible with Airbyte,
    convert Databend timestamp string to Airbyte.
    Databend stores dates in YYYY-MM-DD HH:mm:SS format.
    Airbyte requires YYYY-MM-DDTHH:mm:SS.

    :return: List of the same data as passed that's been converted to compatible types.
        https://docs.airbyte.com/understanding-airbyte/supported-data-types/#the-types
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


def airbyte_message_from_data(raw_data: List[Any], columns: List[str], table_name: str) -> Optional[AirbyteMessage]:
    """
    Wrap data into an AirbyteMessage.

    :param raw_data: Raw data row returned from a fetch query. Each item in the list
        represents a row of data.
        Example: [10, "Oranges"]
    :param columns: List of column names
        Example: ["Quantity", "Fruit"]
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
