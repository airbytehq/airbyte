#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def format_airbyte_time(d: datetime):
    s = f"{d}"
    s = s.split(".")[0]
    s = s.replace(" ", "T")
    s += "+00:00"
    return s
