#!/usr/bin/env python3
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import hashlib
import json
import sys
from typing import Any


def _generate_hash(value: Any) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()


def obfuscate(value: Any) -> Any:
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
        else:
            if data.get("type") == "RECORD":
                record_data = data["record"].get("data", {})
                obfuscated_record = {k: obfuscate(v) for k, v in record_data.items()}
                data["record"]["data"] = obfuscated_record
            sys.stdout.write(f"{json.dumps(data)}\n")
