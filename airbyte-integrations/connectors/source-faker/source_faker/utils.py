#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.models import AirbyteEstimateTraceMessage, AirbyteTraceMessage, EstimateType, TraceType


def read_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.loads(f.read())
    except (OSError, json.JSONDecodeError) as exc:
        message = "Bundled dataset file is unreadable or malformed."
        raise AirbyteTracedException(message=message, failure_type=FailureType.system_error) from exc


def format_airbyte_time(d: datetime):
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
