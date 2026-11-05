# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import CONFIG, NOW, check, error, fixture_record, list_request, page, run, search_request


REGIONS = [("us", "https://api.usepylon.com"), ("eu", "https://api.eu.usepylon.com")]


@pytest.mark.parametrize("region,base", REGIONS)
@pytest.mark.parametrize("stream", ["tags", "issues", "issue_messages"])
@pytest.mark.parametrize("empty", [False, True])
@freeze_time(NOW)
def test_regional_reads(region: str, base: str, stream: str, empty: bool) -> None:
    record = fixture_record(stream)
    with HttpMocker() as mocker:
        if stream == "tags":
            request = list_request("tags", base=base)
            mocker.get(request, page([] if empty else [record]))
        else:
            request = search_request(base=base)
            parent = fixture_record("issues")
            mocker.post(request, page([] if empty else [parent]))
            if stream == "issue_messages" and not empty:
                mocker.get(list_request(f"issues/{parent['id']}/messages", base=base), page([record]))
        output = run(stream, cfg={**CONFIG, "region": region})
        mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert len(output.records) == (0 if empty else 1)
    if not empty:
        assert output.records[0].record.data["id"] == record["id"]


@pytest.mark.parametrize("region,base", REGIONS)
@pytest.mark.parametrize("valid", [True, False])
@freeze_time(NOW)
def test_regional_check(region: str, base: str, valid: bool) -> None:
    with HttpMocker() as mocker:
        request = list_request("tags", base=base)
        mocker.get(request, page([]) if valid else error(401, "invalid_api_token"))
        output = check({**CONFIG, "region": region})
        mocker.assert_number_of_calls(request, 1)
    assert output.connection_status_messages[0].connectionStatus.status == (Status.SUCCEEDED if valid else Status.FAILED)


@freeze_time(NOW)
def test_region_defaults_to_us() -> None:
    config = CONFIG.copy()
    with HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, page([]))
        output = run("tags", cfg=config)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors == []


@pytest.mark.parametrize("region,base", REGIONS)
@freeze_time(NOW)
def test_wrong_region_remediation(region: str, base: str) -> None:
    with HttpMocker() as mocker:
        request = list_request("tags", base=base)
        mocker.get(request, error(401, "wrong_region_token"))
        output = run("tags", cfg={**CONFIG, "region": region}, expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    assert any(
        message.trace.error.failure_type == FailureType.config_error
        and "Set Region to match the token: pylon_api_eu_ means EU, pylon_api_ means US, and older unprefixed tokens use the region where the Pylon tenant is hosted." in message.trace.error.message
        for message in output.errors
    )
