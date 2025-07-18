#!/usr/bin/env python3
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any


#
# record_obfuscator is a tiny script that:
# 1. reads JSON lines from stdin
# 2. obfuscates the data in AirbyteRecordMessage lines
# 3. spits obfuscated lines back to stdout
# All stdin lines that are not type: RECORD remain unchanged.
#
# It's used in live-tests (airbyte-ci/connectors/live-tests) to be able to dump raw data from a live connection
# without leaking actual sensitive production data.
#
# The script is copied over into the live tests runnder dagger container.
#


def _generate_hash(value: Any) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()


def obfuscate(value: Any) -> Any:
    """Returns an obfuscated version of the input value while retaiining it's type and length information."""
    if isinstance(value, str):
        obfuscated_value = f"string_len-{len(value)}_" + _generate_hash(value)
    elif isinstance(value, int):
        obfuscated_value = f"integer_len-{len(str(value))}" + _generate_hash(value)
    elif isinstance(value, float):
        obfuscated_value = f"number_len-{len(str(value))}" + _generate_hash(value)
    elif isinstance(value, bool):
        obfuscated_value = "boolean_" + _generate_hash(value)
    elif value is None:
        obfuscated_value = "null_" + _generate_hash(value)
    elif isinstance(value, list):
        obfuscated_value = f"array_len-{len(value)}" + _generate_hash(json.dumps(value, sort_keys=True).encode())
    elif isinstance(value, dict):
        obfuscated_value = f"object_len-{len(value.keys())}" + _generate_hash(json.dumps(value, sort_keys=True).encode())
    else:
        raise ValueError(f"Unsupported data type: {type(value)}")

    return obfuscated_value


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        try:
            data = json.loads(line)
        except Exception as exc:
            # We don't expect invalid json so if we see it, it will go to stderr
            sys.stderr.write(f"{line}\n")

        # try / except / else: Else block runs only if no exceptions were raised.
        else:
            if data.get("type") == "RECORD":
                record_data = data["record"].get("data", {})
                obfuscated_record = {k: obfuscate(v) for k, v in record_data.items()}
                data["record"]["data"] = obfuscated_record
            sys.stdout.write(f"{json.dumps(data)}\n")
