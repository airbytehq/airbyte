import json
import subprocess
import tempfile

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_protocol.models import AirbyteLogMessage, AirbyteMessage, AirbyteStreamStatus, ConfiguredAirbyteCatalog, Level, TraceType, Type


def _validate_state_messages_order(stream_name: str, output: EntrypointOutput):
    current_cursor_value = None
    for message in output.state_messages:
        if stream_name == message.state.stream.stream_descriptor.name:
            cursor_value = _get_state_value(message, stream_name)
            if not cursor_value:
                continue

            if current_cursor_value:
                assert cursor_value >= current_cursor_value
            current_cursor_value = cursor_value


def _get_state_value(message, stream_name):
    # assumes state format is `{<stream_name>: {<cursor_field>: <cursor_value>}}`
    try:
        return list(message.state.data[stream_name].values())[0]
    except:
        # if there are no records in the slice, it can return a state with format `{}`
        return None


if __name__ == "__main__":
    """
    Note that debug mode can't be enabled as thread write to stdout which screws the stdout. For example, `HttpRequester._send`
    """
    stream_name = "customers"
    first_incremental_result = subprocess.run(
        ["source activate .venv/bin/activate; SKIP_CONCURRENCY=true python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    )

    first_incremental_output = EntrypointOutput(first_incremental_result.stdout.decode().split("\n"))
    _validate_state_messages_order(stream_name, first_incremental_output)

    for x in range(len(first_incremental_output.state_messages)):
        start_capturing = False
        state_messages_count = 0
        record_count = 0

        checkpoint = first_incremental_output.state_messages[x]
        state_file = [{
            "type": "STREAM",
            "stream": {
                "stream_state": checkpoint.state.data[stream_name],
                "stream_descriptor": {"name": stream_name}
            }
        }]
        for message in first_incremental_output._messages:
            if start_capturing and message.type == Type.RECORD:
                record_count += 1
            elif message.type == Type.STATE:
                state_messages_count += 1
                if state_messages_count == x + 1:
                    start_capturing = True


        with tempfile.NamedTemporaryFile(mode="w+") as tmp:
            json.dump(state_file, tmp.file)
            tmp.flush()

            result = subprocess.run(
                [f"source activate .venv/bin/activate; python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state {tmp.name}"],
                capture_output=True,
                shell=True,
                executable="/bin/bash"
            )
            assert result.returncode == 0

        incremental_output = EntrypointOutput(result.stdout.decode().split("\n"))
        _validate_state_messages_order(stream_name, incremental_output)

        assert len(incremental_output.records) == record_count

