from pydantic import BaseModel
from enum import Enum


class LogsStreamDataType(Enum):
    EVENT = 'event'
    INSTALLATION = 'installation'
    SESSION_START = 'session_start'
    PUSH_TOKEN = 'push_token'
    CRASH = 'crash'
    ERROR = 'error'


class LogsStreamWindow(BaseModel):
    # TODO safe_to_load
    stream_window_timestamp: int
    export_schema_id: int
    payload_bytes: int
    event_count: int
    update_timestamp: int


class LogsStream(BaseModel):
    data_type: LogsStreamDataType
    stream_windows: list[LogsStreamWindow]


class LogsStreamSchema(BaseModel):
    export_schema_id: int
    export_format: str
    field_names: list[str]


class LogsStreamsStatus(BaseModel):
    streams: list[LogsStream]
    export_fields: list[LogsStreamSchema]