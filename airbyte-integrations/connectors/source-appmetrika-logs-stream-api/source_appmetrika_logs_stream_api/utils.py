from typing import Any, Mapping
import math


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def filename_from_slice_window(slice_window: Mapping[str, Any]) -> str:
    return f'output/{slice_window["export_schema_id"]}_{slice_window["stream_window_timestamp"]}.csv'
