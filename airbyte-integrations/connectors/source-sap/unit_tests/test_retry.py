"""Retry policy for transient SAP failures.

The CDK's backoff machinery is HTTP-only, so this is ours. SAP hands out
RESOURCE_FAILURE and RFC_COMMUNICATION_FAILURE whenever the system is briefly out
of work processes, which is routine on a busy system and should not fail a sync.
"""

import pytest

from source_sap.retry import retry_transient


class Boom(Exception):
    pass


def test_a_successful_call_is_not_retried():
    calls = []

    @retry_transient(attempts=3, base_delay=0)
    def work():
        calls.append(1)
        return "ok"

    assert work() == "ok"
    assert len(calls) == 1


def test_a_transient_failure_is_retried_then_succeeds():
    calls = []

    @retry_transient(attempts=3, base_delay=0)
    def work():
        calls.append(1)
        if len(calls) < 3:
            raise Boom("RFC_COMMUNICATION_FAILURE: no free work process")
        return "ok"

    assert work() == "ok"
    assert len(calls) == 3


def test_a_config_error_is_not_retried():
    calls = []

    @retry_transient(attempts=5, base_delay=0)
    def work():
        calls.append(1)
        raise Boom("RFC_LOGON_FAILURE: Name or password is incorrect")

    with pytest.raises(Boom):
        work()
    # Retrying a wrong password just locks the SAP user out.
    assert len(calls) == 1


def test_a_system_error_is_not_retried():
    calls = []

    @retry_transient(attempts=5, base_delay=0)
    def work():
        calls.append(1)
        raise Boom("something unexpected")

    with pytest.raises(Boom):
        work()
    assert len(calls) == 1


def test_attempts_are_exhausted_and_the_last_error_is_raised():
    calls = []

    @retry_transient(attempts=3, base_delay=0)
    def work():
        calls.append(1)
        raise Boom(f"RESOURCE_FAILURE attempt {len(calls)}")

    with pytest.raises(Boom, match="attempt 3"):
        work()
    assert len(calls) == 3


def test_backoff_grows_between_attempts(monkeypatch):
    slept = []
    monkeypatch.setattr("source_sap.retry.time.sleep", slept.append)
    calls = []

    @retry_transient(attempts=4, base_delay=2)
    def work():
        calls.append(1)
        raise Boom("RESOURCE_FAILURE")

    with pytest.raises(Boom):
        work()
    assert slept == [2, 4, 8]
