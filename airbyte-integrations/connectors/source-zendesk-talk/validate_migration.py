# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import hashlib
import json
import os
import subprocess

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from urllib.parse import urlparse, parse_qs


_SOURCE_NAME = os.path.split(os.getcwd())[-1]


class Url:
    def __init__(self, url: str) -> None:
        parsed_url = urlparse(url)
        self._for__str__ = url
        self._scheme = parsed_url.scheme
        self._netloc = parsed_url.netloc
        self._path = parsed_url.path
        self._query_params = parse_qs(parsed_url.query)
        # remove query parameters that you know has changed and want to exclude from the validation
        # self._query_params.pop("statistics", None)

    def __eq__(self, other):
        return self._scheme == other._scheme and self._netloc == other._netloc and self._path == other._path and self._query_params == other._query_params

    def __str__(self):
        return self._for__str__

    def __hash__(self):
        dhash = hashlib.md5()
        dhash.update(json.dumps(self._query_params, sort_keys=True).encode())
        return hash((self._scheme, self._netloc, self._path, dhash.hexdigest()))


def dict_diff(a, b):
    diff = {}
    for k, v in a.items():
        if k not in b:
            diff[k] = v
        elif v != b[k]:
            diff[k] = "%s != %s" % (v, b[k])
    for k, v in b.items():
        if k not in a:
            diff[k] = v

    return diff


def delete_none(_dict):
    """Delete None values recursively from all of the dictionaries as None value and fields not defined means the same thing for Airbyte"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_none(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_none(v_i)

    return _dict


def _run_manifest():
    return subprocess.run(
        [
            "source activate .venv/bin/activate; python main.py read --config secrets/config.json --catalog secrets/configured_catalog.json --debug"
        ],
        capture_output=True,
        shell=True,
        executable="/bin/bash",
    )


def _run_most_recent():
    return subprocess.run(
        [
            f"docker run -v $(pwd)/secrets:/data airbyte/{_SOURCE_NAME} read --config /data/config.json --catalog /data/configured_catalog.json --debug"
        ],
        capture_output=True,
        shell=True,
        executable="/bin/bash",
    )


def _compare_catalogs():
    """
    FIXME
    This methods is not good enough to allow for comparing schemas. The main problem is that order does not matter in comparing schemas
    but the schema is created using python lists and comparing list validates order
    """
    manifest_discover_output = _get_entrypoint_output_from_process(
        subprocess.run(
            ["source activate .venv/bin/activate; python main.py discover --config secrets/config.json --debug"],
            capture_output=True,
            shell=True,
            executable="/bin/bash",
        )
    )
    manifest_catalog = list(filter(lambda message: message.catalog, manifest_discover_output._messages))[0]

    mostrecent_discover_output = _get_entrypoint_output_from_process(
        subprocess.run(
            [f"docker run -v $(pwd)/secrets:/data airbyte/{_SOURCE_NAME} discover --config /data/config.json --debug"],
            capture_output=True,
            shell=True,
            executable="/bin/bash",
        )
    )
    most_recent_catalog = list(filter(lambda message: message.catalog, mostrecent_discover_output._messages))[0]

    for manifest_stream, most_recent_stream in zip(manifest_catalog.catalog.streams, most_recent_catalog.catalog.streams):
        diff = dict_diff(manifest_stream.json_schema, most_recent_stream.json_schema)
        assert (
            manifest_stream.json_schema == most_recent_stream.json_schema
        ), f"Stream {most_recent_stream.name} does not have the same schema: \n{diff}"
    assert manifest_catalog.catalog.streams == most_recent_catalog.catalog.streams


def _get_entrypoint_output_from_process(process_output):
    assert process_output.returncode == 0
    return EntrypointOutput(process_output.stdout.decode().split("\n"))


def _get_entrypoint_output(filename: str) -> EntrypointOutput:
    if "manifest" in filename:
        return _get_entrypoint_output_from_process(_run_manifest())
    return _get_entrypoint_output_from_process(_run_most_recent())


def _print_requests(name, output):
    print(name)
    for outbound_log in _extract_outbound_logs(output):
        print(f"\t{outbound_log.log.message}")


def _compare_requests(manifest_output, mostrecent_output):
    manifest_requests = set(map(lambda request: Url(json.loads(request.log.message)["data"]["url"]), _extract_outbound_logs(manifest_output)))
    mostrecent_requests = set(map(lambda request: Url(json.loads(request.log.message)["data"]["url"]), _extract_outbound_logs(mostrecent_output)))
    assert not manifest_requests.difference(mostrecent_requests)
    assert not mostrecent_requests.difference(manifest_requests)


def _extract_outbound_logs(output):
    return filter(lambda log: "outbound API request" in log.log.message, output.logs)


# _compare_catalogs()

manifest_output = _get_entrypoint_output("manifest")
mostrecent_output = _get_entrypoint_output("mostrecent")

_print_requests("MANIFEST REQUESTS", manifest_output)
_print_requests("MOSTRECENT REQUESTS", mostrecent_output)
_compare_requests(manifest_output, mostrecent_output)

assert len(manifest_output.records) == len(mostrecent_output.records), "Mismatch in the number of records"
if len(manifest_output.records) == 0:
    assert False, "No records were synced. Please validate the stream manually"

for i in range(len(manifest_output.records)):
    manifest_record = delete_none(manifest_output.records[i].record.data)

    pk = ["id"]
    if pk:
        mostrecent_record = next(
            filter(lambda record: all(record.record.data[pk_item] == manifest_record[pk_item] for pk_item in pk), mostrecent_output.records)
        )
    else:
        mostrecent_record = mostrecent_output.records[i]
    mostrecent_record = delete_none(mostrecent_record.record.data)

    if manifest_record != mostrecent_record:
        assert False, dict_diff(manifest_record, mostrecent_record)


print(f"{len(manifest_output.records)} records were compared")

if (
    manifest_output.state_messages and manifest_output.state_messages[-1].state.stream.stream_state.json() != "{}"
) or mostrecent_output.state_messages:
    assert manifest_output.state_messages[-1].state.stream.stream_state == mostrecent_output.state_messages[-1].state.stream.stream_state
