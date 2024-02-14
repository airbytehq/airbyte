# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import sys

sample_catalog = {
    "type": "CATALOG",
    "catalog": {
        "streams": [
            {
                "name": "stream1",
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_cursor": True,
                "default_cursor_field": ["column1"],
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "column1": {"type": "string"},
                        "column2": {"type": "number"},
                    },
                },
            },
            {
                "name": "stream2",
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_cursor": False,
                "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "column1": {"type": "string"},
                        "column2": {"type": "number"},
                        "empty_column": {"type": "string"},
                    },
                },
            },
        ]
    },
}

sample_connection_specification = {
    "type": "SPEC",
    "spec": {
        "documentationUrl": "https://example.com",
        "connectionSpecification": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "apiKey": {
                    "type": "string",
                    "title": "API Key",
                    "description": "The API key for the service",
                }
            },
        },
    },
}

sample_connection_check_success = {
    "type": "CONNECTION_STATUS",
    "connectionStatus": {"status": "SUCCEEDED"},
}

sample_connection_check_failure = {
    "type": "CONNECTION_STATUS",
    "connectionStatus": {"status": "FAILED", "message": "An error"},
}

sample_record1_stream1 = {
    "type": "RECORD",
    "record": {
        "data": {"column1": "value1", "column2": 1},
        "stream": "stream1",
        "emitted_at": 123456789,
    },
}
sample_record2_stream1 = {
    "type": "RECORD",
    "record": {
        "data": {"column1": "value2", "column2": 2},
        "stream": "stream1",
        "emitted_at": 123456789,
    },
}
sample_record_stream2 = {
    "type": "RECORD",
    "record": {
        "data": {"column1": "value1", "column2": 1},
        "stream": "stream2",
        "emitted_at": 123456789,
    },
}


def parse_args():
    arg_dict = {}
    args = sys.argv[2:]
    for i in range(0, len(args), 2):
        arg_dict[args[i]] = args[i + 1]

    return arg_dict


def get_json_file(path):
    with open(path, "r") as f:
        return json.load(f)


def run():
    args = sys.argv[1:]
    if args[0] == "spec":
        print(json.dumps(sample_connection_specification))
    elif args[0] == "discover":
        print(json.dumps(sample_catalog))
    elif args[0] == "check":
        args = parse_args()
        config = get_json_file(args["--config"])
        if config.get("apiKey").startswith("test"):
            print(json.dumps(sample_connection_check_success))
        else:
            print(json.dumps(sample_connection_check_failure))
    elif args[0] == "read":
        args = parse_args()
        catalog = get_json_file(args["--catalog"])
        config = get_json_file(args["--config"])
        print(json.dumps({"type": "LOG", "log": {"level": "INFO", "message": "Starting sync"}}))
        for stream in catalog["streams"]:
            if stream["stream"]["name"] == "stream1":
                print(json.dumps(sample_record1_stream1))
                if config.get("apiKey") == "test_fail_during_sync":
                    raise Exception("An error")
                print(json.dumps(sample_record2_stream1))
            elif stream["stream"]["name"] == "stream2":
                print(json.dumps(sample_record_stream2))
