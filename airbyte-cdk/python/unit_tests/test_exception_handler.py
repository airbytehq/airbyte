#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import subprocess
import sys

import pytest
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteLogMessage, AirbyteMessage, AirbyteTraceMessage


def test_uncaught_exception_handler():
    cmd = "from airbyte_cdk.logger import init_logger; from airbyte_cdk.exception_handler import init_uncaught_exception_handler; logger = init_logger('airbyte'); init_uncaught_exception_handler(logger); raise 1"
    exception_message = "exceptions must derive from BaseException"
    exception_trace = (
        "Traceback (most recent call last):\n"
        '  File "<string>", line 1, in <module>\n'
        "TypeError: exceptions must derive from BaseException"
    )

    expected_log_message = AirbyteMessage(
        type="LOG", log=AirbyteLogMessage(level="FATAL", message=f"{exception_message}\n{exception_trace}")
    )

    expected_trace_message = AirbyteMessage(
        type="TRACE",
        trace=AirbyteTraceMessage(
            type="ERROR",
            emitted_at=0.0,
            error=AirbyteErrorTraceMessage(
                failure_type="system_error",
                message="Something went wrong in the connector. See the logs for more details.",
                internal_message=exception_message,
                stack_trace=f"{exception_trace}\n",
            ),
        ),
    )

    with pytest.raises(subprocess.CalledProcessError) as err:
        subprocess.check_output([sys.executable, "-c", cmd], stderr=subprocess.STDOUT)

    assert not err.value.stderr, "nothing on the stderr"

    stdout_lines = err.value.output.decode("utf-8").strip().split("\n")
    assert len(stdout_lines) == 2

    log_output, trace_output = stdout_lines

    out_log_message = AirbyteMessage.parse_obj(json.loads(log_output))
    assert out_log_message == expected_log_message, "Log message should be emitted in expected form"

    out_trace_message = AirbyteMessage.parse_obj(json.loads(trace_output))
    assert out_trace_message.trace.emitted_at > 0
    out_trace_message.trace.emitted_at = 0.0  # set a specific emitted_at value for testing
    assert out_trace_message == expected_trace_message, "Trace message should be emitted in expected form"
