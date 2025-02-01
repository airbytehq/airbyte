#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
from typing import Union

from airbyte_cdk.models import AirbyteEstimateTraceMessage, AirbyteTraceMessage, EstimateType, TraceType


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def format_airbyte_time(d: Union[datetime.datetime, str]):
    s = f"{d}"
    s = s.split(".")[0]
    s = s.replace(" ", "T")
    s += "+00:00"
    return s


def now_millis():
    return int(datetime.datetime.now().timestamp() * 1000)


def generate_estimate(stream_name: str, total: int, bytes_per_row: int):
    emitted_at = int(datetime.datetime.now().timestamp() * 1000)
    estimate_message = AirbyteEstimateTraceMessage(
        type=EstimateType.STREAM, name=stream_name, row_estimate=round(total), byte_estimate=round(total * bytes_per_row)
    )
    return AirbyteTraceMessage(type=TraceType.ESTIMATE, emitted_at=emitted_at, estimate=estimate_message)
