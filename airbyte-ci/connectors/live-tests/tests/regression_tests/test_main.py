from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from live_tests.regression_tests.main import COMMANDS, _dispatch, _do_test_run


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, expected_calls",
    [
        pytest.param(command, [command, command], id=f"{command}-runs") for command in COMMANDS
    ] + [
        pytest.param("all", COMMANDS * 2, id="all-runs-all-commands")  # Expect each command in COMMANDS to be called twice (for control and target)
    ],
)
async def test_do_test_run(command, expected_calls):
    control_connector_mock = MagicMock()
    control_connector_mock.container = MagicMock()
    control_connector_mock.version = "control_version"

    target_connector_mock = MagicMock()
    target_connector_mock.container = MagicMock()
    target_connector_mock.version = "target_version"

    _dispatch_mock = AsyncMock()

    with patch('regression_testing.main._dispatch', _dispatch_mock):
        await _do_test_run(
            control_connector=control_connector_mock,
            target_connector=target_connector_mock,
            output_directory="/tmp/output",
            command=command,
            config=None,
            catalog=None,
            state=None,
        )

    actual_calls = [_dispatch_mock.call_args_list[i][0][3] for i in range(len(_dispatch_mock.call_args_list))]
    assert sorted(actual_calls) == sorted(expected_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, expected_error, expected_method",
    [
        pytest.param("check", None, "call_check", id="check-is-called"),
        pytest.param("discover", None, "call_discover", id="discover-is-called"),
        pytest.param("read", None, "call_read", id="read-is-called"),
        pytest.param("read-with-state", None, "call_read_with_state", id="read-with-state-is-called"),
        pytest.param("spec", None, "call_spec", id="spec-is-called"),
        pytest.param("all", NotImplementedError, None, id="all-is-not-called"),
        pytest.param("x", NotImplementedError, None, id="nonexistant-command-is-not-called"),
    ],
)
async def test_dispatch(command, expected_error, expected_method):
    container_mock = MagicMock()
    backend_mock = MagicMock()
    runner_mock = MagicMock()
    runner_mock.call_check = AsyncMock()
    runner_mock.call_discover = AsyncMock()
    runner_mock.call_read = AsyncMock()
    runner_mock.call_read_with_state = AsyncMock()
    runner_mock.call_spec = AsyncMock()

    # Patching the ConnectorRunner to return our mock
    with patch('regression_testing.main.ConnectorRunner', return_value=runner_mock):
        if expected_error:
            with pytest.raises(expected_error):
                await _dispatch(container_mock, backend_mock, "/tmp/output", command, None, None, None)
        else:
            await _dispatch(container_mock, backend_mock, "/tmp/output", command, None, None, None)
            getattr(runner_mock, expected_method).assert_awaited_once()
