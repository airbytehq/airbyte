import json
import logging
import subprocess
import sys
import tempfile

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_protocol.models import Type


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _validate_state_messages_order(stream_name: str, output: EntrypointOutput):
    assert len(output.state_messages), "No state messages were emitted"

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


def _get_distinct_ids(records):
    # assumed primary key is "id"
    return set(map(lambda message: message.record.data["id"], records))


def _compare_records(actual, expected):
    actual_ids = _get_distinct_ids(actual)
    expected_ids = _get_distinct_ids(expected)

    missing_expected = expected_ids - actual_ids
    if missing_expected:
        logger.error(f"Missing expected records: {missing_expected}")
        assert not missing_expected

    non_expected_actual = actual_ids - expected_ids
    if non_expected_actual:
        # No assertion to be done here:
        # As we execute actual after expected, we might have actual records that were not in expected. This is normal but does not seem possible to avoid.
        logger.warning(f"Actual records that were not expected: {non_expected_actual}")

    logging.info("Actual and expected logs are aligned, yay!")


if __name__ == "__main__":
    """
    Note that debug mode can't be enabled as thread write to stdout which screws the stdout. For example, `HttpRequester._send`
    """
    stream_name = "customers"

    logger.info(f"Starting state validation for stream `{stream_name}`...")
    logger.debug(f"First incremental sync...")
    first_incremental_without_concurrency_result = subprocess.run(
        ["source activate .venv/bin/activate; SKIP_CONCURRENCY=true python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    )
    assert first_incremental_without_concurrency_result.returncode == 0
    first_incremental_without_concurrency_output = EntrypointOutput(first_incremental_without_concurrency_result.stdout.decode().split("\n"))
    assert len(first_incremental_without_concurrency_output.state_messages), "There should at least be one state message emitted by the non-concurrent first incremental sync in order to allow for further testing"
    state_messages = first_incremental_without_concurrency_output.state_messages

    first_incremental_with_concurrency_result = subprocess.run(
        ["source activate .venv/bin/activate; python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json"],
        capture_output=True,
        shell=True,
        executable="/bin/bash"
    )
    assert first_incremental_with_concurrency_result.returncode == 0
    first_incremental_with_concurrency_output = EntrypointOutput(first_incremental_with_concurrency_result.stdout.decode().split("\n"))

    _validate_state_messages_order(stream_name, first_incremental_with_concurrency_output)
    _compare_records(first_incremental_with_concurrency_output.records, first_incremental_without_concurrency_output.records)

    for x in range(len(state_messages)):
        checkpoint = state_messages[x]
        logger.info(f"Validating using state #{checkpoint}#...")
        state_file = [{
            "type": "STREAM",
            "stream": {
                "stream_state": checkpoint.state.data[stream_name],
                "stream_descriptor": {"name": stream_name}
            }
        }]

        with tempfile.NamedTemporaryFile(mode="w+") as tmp:
            json.dump(state_file, tmp.file)
            tmp.flush()

            without_concurrency_result = subprocess.run(
                [f"source activate .venv/bin/activate; SKIP_CONCURRENCY=true python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state {tmp.name}"],
                capture_output=True,
                shell=True,
                executable="/bin/bash"
            )
            assert without_concurrency_result.returncode == 0
            without_concurrency_output = EntrypointOutput(without_concurrency_result.stdout.decode().split("\n"))

            with_concurrency_result = subprocess.run(
                [f"source activate .venv/bin/activate; python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state {tmp.name}"],
                capture_output=True,
                shell=True,
                executable="/bin/bash"
            )
            assert with_concurrency_result.returncode == 0
            with_concurrency_output = EntrypointOutput(with_concurrency_result.stdout.decode().split("\n"))

        _validate_state_messages_order(stream_name, with_concurrency_output)

        _compare_records(with_concurrency_output.records, without_concurrency_output.records)
