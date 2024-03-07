import subprocess

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput


def dict_diff(a, b):
    diff = {}
    for k,v in a.items():
        if k not in b:
            diff[k] = v
        elif v != b[k]:
            diff[k] = '%s != %s' % (v, b[k])
    for k,v in b.items():
        if k not in a:
            diff[k] = v

    return diff


def _run_manifest():
    return subprocess.run(
        [
        "source activate .venv/bin/activate; python main.py read --config secrets/config.json --catalog secrets/configured_catalog.json --debug"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    )

def _run_most_recent():
    return subprocess.run(
        [
        "docker run -v $(pwd)/secrets:/data airbyte/source-sentry read --config /data/config.json --catalog /data/configured_catalog.json --debug"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    )

def _compare_catalogs():
    manifest_discover_output = _get_entrypoint_output_from_process(subprocess.run(
        ["source activate .venv/bin/activate; python main.py discover --config secrets/config.json --debug"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    ))
    manifest_catalog = list(filter(lambda message: message.catalog, manifest_discover_output._messages))[0]

    mostrecent_discover_output = _get_entrypoint_output_from_process(subprocess.run(
        ["docker run -v $(pwd)/secrets:/data airbyte/source-zendesk-talk discover --config /data/config.json --debug"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    ))
    most_recent_catalog = list(filter(lambda message: message.catalog, mostrecent_discover_output._messages))[0]

    for manifest_stream, most_recent_stream in zip(manifest_catalog.catalog.streams, most_recent_catalog.catalog.streams):
        diff = dict_diff(manifest_stream.json_schema, most_recent_stream.json_schema)
        assert manifest_stream.json_schema == most_recent_stream.json_schema, f"Stream {most_recent_stream.name} does not have the same schema: \n{diff}"
    assert manifest_catalog.catalog.streams == most_recent_catalog.catalog.streams


def _get_entrypoint_output_from_process(process_output):
    assert process_output.returncode == 0
    return EntrypointOutput(process_output.stdout.decode().split("\n"))


def _get_entrypoint_output(filename: str) -> EntrypointOutput:
    if "manifest" in filename:
        return _get_entrypoint_output_from_process(_run_manifest())
    return _get_entrypoint_output_from_process(_run_most_recent())


def print_requests(name, output):
    print(name)
    for outbound_log in filter(lambda log: "outbound API request" in log.log.message, output.logs):
        print(f"\t{outbound_log.log.message}")

_compare_catalogs()

manifest_output = _get_entrypoint_output("manifest")
mostrecent_output = _get_entrypoint_output("mostrecent")

print_requests("MANIFEST REQUESTS", manifest_output)
print_requests("MOSTRECENT REQUESTS", mostrecent_output)

assert len(manifest_output.records) == len(mostrecent_output.records), "Mismatch in the number of records"
if len(manifest_output.records) == 0:
    assert False, "No records were synced. Please validate the stream manually"

for i in range(len(manifest_output.records)):
    if manifest_output.records[i].record.data != mostrecent_output.records[i].record.data:
        assert False, dict_diff(manifest_output.records[i].record.data, mostrecent_output.records[i].record.data)


print(f"{len(manifest_output.records)} records were compared")

if (manifest_output.state_messages and manifest_output.state_messages[-1].state.stream.stream_state.json() != "{}") or mostrecent_output.state_messages:
    assert manifest_output.state_messages[-1].state.stream.stream_state == mostrecent_output.state_messages[-1].state.stream.stream_state
