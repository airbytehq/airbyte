# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the Pipedrive error handlers declared in `manifest.yaml`.

Pipedrive returns a JSON envelope `{"success": false, "error": "..."}` for most failures, but
repeated rate-limit abuse can also produce a Cloudflare HTML 403 with no JSON body. These tests
assert how each status code is classified (fail / ignore / retry / rate-limited), that the
user-facing messages include Pipedrive's `error` text when present, and that substreams skip a
single missing or inaccessible parent instead of failing the whole sync.
"""

import json
import logging

import pytest
import requests
import yaml
from _helpers import (
    CONFIG,
    collection,
    deals_archived_request,
    deals_request,
    empty_v2_page,
    get_source,
    pipedrive_error,
    read_stream,
    request,
)

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip real waits and record the requested durations."""
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _error_trace(output):
    """Return the stream-level error trace (the last trace is the aggregated 'streams did not sync' summary)."""
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


def test_manifest_has_no_composite_error_handler() -> None:
    from conftest import _YAML_FILE_PATH

    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers


def test_401_fails_as_config_error_with_pipedrive_error_text() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(401, "unauthorized access"))

        output = read_stream("deals", expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "401: unauthorized access" in error.message
        assert "Personal preferences > API" in error.message
        http_mocker.assert_number_of_calls(deals, 1)


def test_check_with_invalid_token_returns_401_config_message() -> None:
    with HttpMocker() as http_mocker:
        # The check stream is `currencies` (#85764); `deals` is kept for manifests that still check on it.
        http_mocker.get(request("v1/currencies", {"limit": "50"}), pipedrive_error(401, "unauthorized access"))
        http_mocker.get(deals_request(), pipedrive_error(401, "unauthorized access"))

        status = get_source().check(logging.getLogger("airbyte"), CONFIG)

        assert status.status == Status.FAILED
        assert "Pipedrive rejected the API token (401: unauthorized access)" in status.message


def test_402_fails_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(402, "company account not open"))

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "402: company account not open" in error.message
        assert "billing" in error.message


def test_403_fails_as_config_error_with_pipedrive_error_text() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(403, "You do not have permissions to do this."))

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "403: You do not have permissions to do this." in error.message


def test_403_html_body_from_cloudflare_still_produces_readable_message() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            HttpResponse(body="<html><body>Access denied</body></html>", status_code=403, headers={"Content-Type": "text/html"}),
        )

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "Pipedrive refused the request (403: forbidden)." in error.message
        assert "Cloudflare" in error.message


def test_429_is_rate_limited_and_retried_after_ratelimit_reset() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        # Spare burst calls, as in the next test: a zero `x-ratelimit-remaining` drains the budget (covered in
        # test_api_budget.py), and with `time.sleep` patched out fast machines give up before the window rolls.
        http_mocker.get(
            deals,
            [
                pipedrive_error(429, "request over limit", headers={"x-ratelimit-reset": "2", "x-ratelimit-remaining": "19"}),
                collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]),
            ],
        )

        output = read_stream("deals")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(deals, 2)


def test_429_exhausting_retries_fails_as_rate_limited() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        # A 429 without `x-ratelimit-remaining` tells the API budget that zero calls are left and fills its
        # moving-window bucket; with `time.sleep` patched out the budget then gives up before the eleventh
        # request on fast machines. Reporting spare burst calls keeps the test on the retry path it targets:
        # the daily token budget is exhausted while the 2-second window still has room.
        http_mocker.get(
            deals,
            pipedrive_error(429, "request over limit", headers={"x-ratelimit-reset": "2", "x-ratelimit-remaining": "19"}),
        )

        output = read_stream("deals", expecting_exception=True)

        assert output.errors
        # max_retries: 10 -> 1 initial attempt + 10 retries; the CDK then gives up with its generic backoff exception,
        # so the Pipedrive-specific hint about the daily budget is surfaced through the logs.
        http_mocker.assert_number_of_calls(deals, 11)
        assert output.is_in_logs("daily API token budget")


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_5xx_is_retried(status_code: int) -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            [
                pipedrive_error(status_code, None),
                collection([{"id": 7, "update_time": "2024-02-01 00:00:00"}]),
            ],
        )

        output = read_stream("deals")

        assert not output.errors
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(deals, 2)


def _deal_products_batch(*deal_ids: int):
    return request("api/v2/deals/products", {"deal_ids": ",".join(map(str, deal_ids)), "limit": "500"})


def _deal_flow_request(deal_id: int):
    return request(f"v1/deals/{deal_id}/flow", {"limit": "500", "items": "dealChange", "all_changes": "1"})


@pytest.mark.parametrize(
    "status_code, error",
    [
        (403, "You do not have permissions to do this."),
        (404, "Deal not found"),
        (410, "Deal has been deleted"),
    ],
)
def test_deal_flow_skips_missing_or_forbidden_parent_deal(status_code: int, error: str) -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(
            deals,
            collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}, {"id": 2, "update_time": "2024-02-01 00:00:00"}]),
        )
        missing_deal = _deal_flow_request(1)
        http_mocker.get(missing_deal, pipedrive_error(status_code, error))
        http_mocker.get(
            _deal_flow_request(2),
            collection(
                [
                    {
                        "object": "dealChange",
                        "timestamp": "2024-02-01 00:00:00",
                        "data": {"id": 20, "item_id": 2, "log_time": "2024-02-01 00:00:00"},
                    }
                ]
            ),
        )

        output = read_stream("deal_flow")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [20]
        http_mocker.assert_number_of_calls(missing_deal, 1)
        assert output.is_in_logs(error)


def test_deal_products_still_fails_on_401() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals, collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        http_mocker.get(_deal_products_batch(1), pipedrive_error(401, "unauthorized access"))

        error = _error_trace(read_stream("deal_products", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "401: unauthorized access" in error.message


def _mail_threads_request(folder: str):
    return request("v1/mailbox/mailThreads", {"folder": folder, "limit": "50"})


def _mail_messages_request(thread_id: int):
    return request(f"v1/mailbox/mailThreads/{thread_id}/mailMessages", {"limit": "50"})


def test_mail_skips_missing_parent_thread() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_mail_threads_request("inbox"), collection([{"id": 10}, {"id": 11}]))
        for folder in ("drafts", "sent", "archive"):
            http_mocker.get(_mail_threads_request(folder), collection([]))
        http_mocker.get(_mail_messages_request(10), pipedrive_error(404, "Mail thread not found"))
        http_mocker.get(_mail_messages_request(11), collection([{"id": 110, "mail_thread_id": 11}]))

        output = read_stream("mail")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [110]


@pytest.mark.parametrize(
    "status_code, error, failure_type, hint",
    [
        # https://pipedrive.readme.io/docs/core-api-concepts-http-status-codes: 415 "Feature is not enabled"
        (415, "Feature is not enabled", FailureType.config_error, "Enable the feature in Pipedrive company settings"),
        # 501 "Non-existent functionality": the connector sent a request Pipedrive does not implement
        (501, "Not implemented", FailureType.system_error, "connector defect"),
        (410, "Gone", FailureType.system_error, "permanently removed"),
    ],
)
def test_statuses_outside_the_cdk_mapping_fail_once_with_pipedrive_text(status_code, error, failure_type, hint) -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(status_code, error))

        error_trace = _error_trace(read_stream("deals", expecting_exception=True))

        assert error_trace.failure_type == failure_type
        assert f"{status_code}: {error}" in error_trace.message
        assert hint in error_trace.message
        http_mocker.assert_number_of_calls(deals, 1)


def test_child_stream_402_reaches_the_shared_handler_instead_of_retrying() -> None:
    # The substream handler only ignores missing or hidden parents; its shared payment_required filter
    # fails a 402 once as config_error instead of the CDK fallback retry.
    with HttpMocker() as http_mocker:
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals_request(), collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        child = _deal_flow_request(1)
        http_mocker.get(child, pipedrive_error(402, "Required suites missing"))

        error = _error_trace(read_stream("deal_flow", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "402: Required suites missing" in error.message
        http_mocker.assert_number_of_calls(child, 1)


@pytest.mark.parametrize(
    "stream, paths, query",
    [
        ("projects", ["api/v2/projects", "api/v2/projects/archived"], {"limit": "500", "status": "open,completed,canceled,deleted"}),
        ("tasks", ["api/v2/tasks"], {"limit": "500"}),
        ("legacy_teams", ["v1/legacyTeams"], {}),
    ],
)
def test_feature_gated_streams_skip_415(stream, paths, query) -> None:
    with HttpMocker() as http_mocker:
        gated_requests = [request(path, query) for path in paths]
        for gated in gated_requests:
            http_mocker.get(gated, pipedrive_error(415, "Feature is not enabled"))

        output = read_stream(stream)

        assert not output.errors
        assert output.records == []
        for gated in gated_requests:
            http_mocker.assert_number_of_calls(gated, 1)


def test_feature_gated_streams_skip_real_plan_responses() -> None:
    # Bodies captured from the test account on 2026-10-12.
    legacy_teams = '{"success":false,"error":"Teams feature is not enabled in your company","error_info":"Please check developers.pipedrive.com","additional_data":null}'
    with HttpMocker() as http_mocker:
        http_mocker.get(request("v1/legacyTeams"), HttpResponse(body=legacy_teams, status_code=403))

        output = read_stream("legacy_teams")

        assert not output.errors
        assert output.is_in_logs("Teams feature is not enabled in your company")


def test_permission_set_without_assignments_is_skipped() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(request("v1/permissionSets", {"limit": "50"}), collection([{"id": "ps-1"}, {"id": "ps-2"}]))
        empty = request("v1/permissionSets/ps-1/assignments", {"limit": "500"})
        http_mocker.get(empty, HttpResponse(body='{"success":false,"error":"Permission set not found."}', status_code=404))
        http_mocker.get(
            request("v1/permissionSets/ps-2/assignments", {"limit": "500"}),
            collection([{"permission_set_id": "ps-2", "user_id": 7}]),
        )

        output = read_stream("permission_set_assignments")

        assert not output.errors
        assert [record.record.data["user_id"] for record in output.records] == [7]
        http_mocker.assert_number_of_calls(empty, 1)


def _templated_response_filters():
    from conftest import _YAML_FILE_PATH

    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    found = {}

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "HttpResponseFilter" and "{{" in str(node.get("error_message", "")):
                found[(tuple(node["http_codes"]), node["error_message"])] = node
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)
    return list(found.values())


_UNEXPECTED_BODIES = {
    "no_error_field": "{}",
    "null_error": '{"success": false, "error": null}',
    "long_error": json.dumps({"success": False, "error": "x" * 5000}),
    "object_error": '{"success": false, "error": {"code": 1}}',
    "list_body": "[1, 2]",
    "null_body": "null",
    "html_body": "<html><body>Access denied</body></html>",
}


@pytest.mark.parametrize("body", list(_UNEXPECTED_BODIES.values()), ids=list(_UNEXPECTED_BODIES))
def test_every_error_message_template_survives_unexpected_bodies(body) -> None:
    filters = _templated_response_filters()
    assert len(filters) >= 15
    for spec in filters:
        response = requests.Response()
        response.status_code = spec["http_codes"][0]
        response._content = body.encode()
        response_filter = HttpResponseFilter(
            action=spec["action"], http_codes=set(spec["http_codes"]), error_message=spec["error_message"], config={}, parameters={}
        )

        message = response_filter.matches(response).error_message

        assert "None" not in message, spec["error_message"]
        # Pipedrive's own text is capped at 300 characters.
        assert "x" * 301 not in message, spec["error_message"]


_CLOUDFLARE_403 = HttpResponse(body="<html><body>Access denied</body></html>", status_code=403, headers={"Content-Type": "text/html"})


@pytest.mark.parametrize("stream", ["deal_products", "deal_flow", "product_variations"])
def test_cloudflare_html_403_on_a_child_stream_fails_instead_of_skipping_the_parent(stream) -> None:
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, _CLOUDFLARE_403)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "Cloudflare" in error.message


_PROJECTS_QUERY = {"limit": "500", "status": "open,completed,canceled,deleted"}


def _mock_gated_stream(http_mocker, stream, response, others=None):
    """Mock the parents of a plan-gated stream and answer its own request(s) with `response` (`others` after the first)."""
    if stream == "legacy_teams":
        targets = [request("v1/legacyTeams")]
    elif stream == "projects":
        targets = [request("api/v2/projects", _PROJECTS_QUERY), request("api/v2/projects/archived", _PROJECTS_QUERY)]
    elif stream == "tasks":
        targets = [request("api/v2/tasks", {"limit": "500"})]
    elif stream == "deal_installments":
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals_request(), collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        targets = [request("api/v2/deals/installments", {"deal_ids": "1", "limit": "500"})]
    elif stream == "permission_set_assignments":
        http_mocker.get(request("v1/permissionSets", {"limit": "50"}), collection([{"id": "ps-1"}]))
        targets = [request("v1/permissionSets/ps-1/assignments", {"limit": "500"})]
    elif stream == "deal_flow":
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals_request(), collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        targets = [_deal_flow_request(1)]
    elif stream == "deal_products":
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals_request(), collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        targets = [_deal_products_batch(1)]
    elif stream == "product_variations":
        http_mocker.get(
            request("api/v2/products", {"limit": "500", "sort_by": "update_time", "sort_direction": "asc"}), collection([{"id": 1}])
        )
        targets = [request("api/v2/products/1/variations", {"limit": "500"})]
    for index, target in enumerate(targets):
        http_mocker.get(target, response if index == 0 or others is None else others)
    return targets


_OWN = [
    "deal_flow",
    "product_variations",
    "deal_products",
    "legacy_teams",
    "projects",
    "tasks",
    "deal_installments",
    "permission_set_assignments",
]


@pytest.mark.parametrize("stream", _OWN)
@pytest.mark.parametrize("status_code", [408, 500, 502, 503, 504])
def test_html_server_errors_are_retried(stream, status_code) -> None:
    html = HttpResponse(body="<html><body>Maintenance</body></html>", status_code=status_code, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, [html, collection([])])

        output = read_stream(stream)

        assert not output.errors
        for target in targets:
            http_mocker.assert_number_of_calls(target, 2)


@pytest.mark.parametrize("stream", _OWN)
def test_html_429_is_rate_limited_and_retried(stream, no_sleep) -> None:
    html = HttpResponse(
        body="<html><body>Rate limited</body></html>",
        status_code=429,
        headers={"Content-Type": "text/html", "x-ratelimit-reset": "2", "x-ratelimit-remaining": "19"},
    )
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, [html, collection([])])

        output = read_stream(stream)

        assert not output.errors
        for target in targets:
            http_mocker.assert_number_of_calls(target, 2)
        # The wait comes from x-ratelimit-reset (2 s plus the CDK's extra second), not from the exponential fallback.
        assert 3 in no_sleep


@pytest.mark.parametrize("stream", _OWN)
def test_401_on_owned_streams_fails_with_the_shared_configuration_message(stream) -> None:
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, pipedrive_error(401, "unauthorized access"))

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "401: unauthorized access" in error.message
        assert "Personal preferences > API" in error.message
        http_mocker.assert_number_of_calls(targets[0], 1)


@pytest.mark.parametrize("stream", _OWN)
def test_429_exhaustion_uses_the_pipedrive_rate_limit_message(stream) -> None:
    response = pipedrive_error(429, "request over limit", headers={"x-ratelimit-reset": "2", "x-ratelimit-remaining": "19"})
    with HttpMocker() as http_mocker:
        # One exhausted partition: projects reads two, and 22 sleepless requests would outrun the 20-per-2s API budget.
        targets = _mock_gated_stream(http_mocker, stream, response, others=collection([]))

        output = read_stream(stream, expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(targets[0], 11)
        assert output.is_in_logs("daily API token budget")


@pytest.mark.parametrize(
    "stream, status_code, error",
    [
        ("tasks", 402, "Company account is not open"),
        ("projects", 403, "Projects access denied"),
        ("tasks", 403, "Tasks access denied"),
        ("deal_installments", 403, "Installments access denied"),
        ("permission_set_assignments", 403, "Assignments access denied"),
        ("product_variations", 403, "Variations access denied"),
        ("product_variations", 404, "Product not found"),
        ("projects", 404, "Projects not found"),
        ("tasks", 404, "Tasks not found"),
    ],
)
def test_stream_specific_ignores_log_the_response_text(stream, status_code, error) -> None:
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, pipedrive_error(status_code, error))

        output = read_stream(stream)

        assert not output.errors
        assert output.records == []
        assert output.is_in_logs(error)


def test_deal_products_410_uses_the_shared_gone_message() -> None:
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, "deal_products", pipedrive_error(410, "Gone"))

        error = _error_trace(read_stream("deal_products", expecting_exception=True))

        assert error.failure_type == FailureType.system_error
        assert "permanently removed (410: Gone)" in error.message
        http_mocker.assert_number_of_calls(targets[0], 1)


@pytest.mark.parametrize("stream", ["deal_flow", "legacy_teams"])
def test_html_200_fails_with_the_cloudflare_message(stream) -> None:
    html = HttpResponse(body="<html><body>Unexpected response</body></html>", status_code=200, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, html)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "Cloudflare" in error.message


_GATED = ["legacy_teams", "projects", "tasks", "deal_installments", "permission_set_assignments"]


@pytest.mark.parametrize("stream", _GATED)
def test_cloudflare_html_403_on_a_plan_gated_stream_fails_instead_of_skipping_it(stream) -> None:
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, _CLOUDFLARE_403)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "Cloudflare" in error.message


@pytest.mark.parametrize(
    "stream, status_code",
    [
        ("legacy_teams", 415),
        ("projects", 402),
        ("projects", 415),
        ("deal_installments", 402),
        ("permission_set_assignments", 404),
    ],
)
def test_plan_responses_with_an_html_body_are_still_skipped(stream, status_code) -> None:
    # Plan statuses and the documented API v1 404 of permission_set_assignments stay skipped whatever the
    # body. An HTML 404 from an API v2 route fails instead (see the next test).
    html = HttpResponse(body="<html><body>Not available</body></html>", status_code=status_code, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, html)

        output = read_stream(stream)

        assert not output.errors
        assert output.records == []


@pytest.mark.parametrize("stream", ["product_variations", "projects", "tasks"])
def test_html_404_from_an_unknown_api_v2_route_fails_instead_of_emptying_the_stream(stream) -> None:
    # API v2 answers a route it does not know with an HTML 404 page; a missing record or a plan response answers with JSON.
    html = HttpResponse(body="<!DOCTYPE html><html><body>Not Found</body></html>", status_code=404, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, stream, html)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "HTML page instead of JSON" in error.message


@pytest.mark.parametrize(
    "stream, status_code",
    [
        ("deal_flow", 400),
        ("deal_flow", 405),
        ("projects", 400),
        ("legacy_teams", 405),
        ("permission_set_assignments", 400),
        ("deal_products", 404),
        ("deal_installments", 404),
    ],
)
def test_html_client_errors_keep_the_cdk_default_classification(stream, status_code) -> None:
    html = HttpResponse(body="<html><body>Error</body></html>", status_code=status_code, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, html)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == FailureType.system_error
        assert f"HTTP Status Code: {status_code}" in error.message
        http_mocker.assert_number_of_calls(targets[0], 1)


@pytest.mark.parametrize("stream", ["deal_flow", "projects"])
@pytest.mark.parametrize("status_code", [505, 507, 520, 522, 524, 530])
def test_html_gateway_errors_beyond_504_are_retried(stream, status_code) -> None:
    html = HttpResponse(body="<html><body>Origin unreachable</body></html>", status_code=status_code, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, [html, collection([])])

        output = read_stream(stream)

        assert not output.errors
        for target in targets:
            http_mocker.assert_number_of_calls(target, 2)


@pytest.mark.parametrize(
    "stream, status_code, text, failure_type",
    [
        ("deal_flow", 501, "501: not implemented", FailureType.system_error),
        ("deal_products", 410, "410: gone", FailureType.system_error),
        ("projects", 410, "410: gone", FailureType.system_error),
        ("legacy_teams", 402, "402: payment required", FailureType.config_error),
        ("permission_set_assignments", 415, "415: feature is not enabled", FailureType.config_error),
        ("deal_installments", 401, "401: unauthorized access", FailureType.config_error),
    ],
)
def test_html_bodies_keep_the_status_specific_message(stream, status_code, text, failure_type) -> None:
    # The HTML guard comes after every status filter, so an HTML body keeps the status's own message.
    html = HttpResponse(body="<html><body>Error</body></html>", status_code=status_code, headers={"Content-Type": "text/html"})
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, html)

        error = _error_trace(read_stream(stream, expecting_exception=True))

        assert error.failure_type == failure_type
        assert text in error.message
        http_mocker.assert_number_of_calls(targets[0], 1)


@pytest.mark.parametrize(
    "stream, status_code, error, failure_type",
    [
        ("legacy_teams", 402, "Company account is not open", FailureType.config_error),
        ("legacy_teams", 501, "Not implemented", FailureType.system_error),
        ("projects", 410, "Gone", FailureType.system_error),
        ("tasks", 410, "Gone", FailureType.system_error),
        ("deal_installments", 410, "Gone", FailureType.system_error),
        ("permission_set_assignments", 402, "Company account is not open", FailureType.config_error),
        ("permission_set_assignments", 415, "Feature is not enabled", FailureType.config_error),
        ("deal_flow", 415, "Feature is not enabled", FailureType.config_error),
        ("deal_flow", 501, "Not implemented", FailureType.system_error),
        ("deal_products", 402, "Company account is not open", FailureType.config_error),
        ("deal_products", 415, "Feature is not enabled", FailureType.config_error),
        ("deal_products", 501, "Not implemented", FailureType.system_error),
        ("projects", 501, "Not implemented", FailureType.system_error),
        ("tasks", 501, "Not implemented", FailureType.system_error),
        ("deal_installments", 501, "Not implemented", FailureType.system_error),
        ("permission_set_assignments", 410, "Gone", FailureType.system_error),
        ("permission_set_assignments", 501, "Not implemented", FailureType.system_error),
        ("product_variations", 402, "Company account is not open", FailureType.config_error),
    ],
)
def test_statuses_missing_from_the_cdk_mapping_reach_the_shared_handler(stream, status_code, error, failure_type) -> None:
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, stream, pipedrive_error(status_code, error))

        error_trace = _error_trace(read_stream(stream, expecting_exception=True))

        assert error_trace.failure_type == failure_type
        assert f"{status_code}: {error}" in error_trace.message
        # Classified once by the shared filter in the per-stream handler, not retried as the CDK fallback would.
        http_mocker.assert_number_of_calls(targets[0], 1)


def test_deal_installments_skip_415() -> None:
    with HttpMocker() as http_mocker:
        _mock_gated_stream(http_mocker, "deal_installments", pipedrive_error(415, "Feature is not enabled"))

        output = read_stream("deal_installments")

        assert not output.errors
        assert output.records == []


@pytest.mark.parametrize("status_code", [404, 410])
def test_deal_products_batch_route_failure_is_not_skipped(status_code) -> None:
    # The batch endpoint answers 200 for deal ids it no longer has, so 404 and 410 mean the route failed.
    with HttpMocker() as http_mocker:
        targets = _mock_gated_stream(http_mocker, "deal_products", pipedrive_error(status_code, "Not found"))

        output = read_stream("deal_products", expecting_exception=True)

        assert _error_trace(output).failure_type == FailureType.system_error
        http_mocker.assert_number_of_calls(targets[0], 1)


def test_deal_products_skips_a_forbidden_batch_and_reads_the_next() -> None:
    # A JSON 403 skips the whole batch of up to 100 deals, as the per-deal route skipped one deal before 4.1.0.
    deals = [{"id": deal_id, "update_time": "2024-02-01 00:00:00"} for deal_id in range(1, 102)]
    with HttpMocker() as http_mocker:
        http_mocker.get(deals_archived_request(), empty_v2_page())
        http_mocker.get(deals_request(), collection(deals))
        http_mocker.get(_deal_products_batch(*range(1, 101)), pipedrive_error(403, "You do not have permissions to do this."))
        http_mocker.get(_deal_products_batch(101), collection([{"id": 1010, "deal_id": 101}]))

        output = read_stream("deal_products")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1010]
        assert output.is_in_logs("You do not have permissions to do this.")


_RETRY_CODES = [408, 500, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530]
# What each per-stream handler does with 402, 404, 410 and 415, for an HTML and for a JSON body. "guard" is the HTML
# guard's failure, "config" a config_error from a status filter, "system" any other failure, "skip" an IGNORE.
_HANDLER_KINDS = {
    "child": {
        "html": {402: "config", 404: "guard", 410: "guard", 415: "config"},
        "json": {402: "config", 404: "skip", 410: "skip", 415: "config"},
    },
    "deal_products": {
        "html": {402: "config", 404: "system", 410: "system", 415: "config"},
        "json": {402: "config", 404: "system", 410: "system", 415: "config"},
    },
    "legacy_teams": {
        "html": {402: "config", 404: "system", 410: "system", 415: "skip"},
        "json": {402: "config", 404: "system", 410: "system", 415: "skip"},
    },
    "projects": {
        "html": {402: "skip", 404: "guard", 410: "system", 415: "skip"},
        "json": {402: "skip", 404: "skip", 410: "system", 415: "skip"},
    },
    "deal_installments": {
        "html": {402: "skip", 404: "system", 410: "system", 415: "skip"},
        "json": {402: "skip", 404: "system", 410: "system", 415: "skip"},
    },
    "permission_set_assignments": {
        "html": {402: "config", 404: "skip", 410: "system", 415: "config"},
        "json": {402: "config", 404: "skip", 410: "system", 415: "config"},
    },
}
_STREAM_KINDS = {
    "deal_flow": "child",
    "mail": "child",
    "product_variations": "child",
    "deal_products": "deal_products",
    "legacy_teams": "legacy_teams",
    "projects": "projects",
    "tasks": "projects",
    "deal_installments": "deal_installments",
    "permission_set_assignments": "permission_set_assignments",
}


def _per_stream_handler(stream):
    from conftest import _YAML_FILE_PATH

    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    definition = next(s for s in manifest["streams"] if s["name"] == stream)["retriever"]["requester"]["error_handler"]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


def _response(status_code, html):
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", "https://api.pipedrive.com/v1/example").prepare()
    response.url = response.request.url
    if html:
        # Cloudflare's real header, so the guard's predicate must match a Content-Type with parameters.
        response.headers["Content-Type"] = "text/html; charset=UTF-8"
        response._content = b"<!DOCTYPE html><html><body>Error</body></html>"
    else:
        response.headers["Content-Type"] = "application/json"
        response._content = b'{"success": false, "error": "Error"}'
    return response


def _outcome(resolution):
    if resolution.response_action != ResponseAction.FAIL:
        return {ResponseAction.IGNORE: "skip", ResponseAction.RETRY: "retry", ResponseAction.RATE_LIMITED: "rate_limited"}.get(
            resolution.response_action, resolution.response_action.name
        )
    if "HTML page instead of JSON" in (resolution.error_message or ""):
        return "guard"
    return "config" if resolution.failure_type == FailureType.config_error else "system"


@pytest.mark.parametrize("stream", list(_STREAM_KINDS))
def test_every_per_stream_handler_classifies_each_status_in_order(stream) -> None:
    # Resolves the handler from the manifest and checks each status a list carries, so a filter that is
    # dropped or moved past the HTML guard changes an outcome.
    handler = _per_stream_handler(stream)
    kind = _HANDLER_KINDS[_STREAM_KINDS[stream]]
    mismatches = []
    for body in ("html", "json"):
        expected = {
            401: "config",
            400: "system",
            405: "system",
            501: "system",
            429: "rate_limited",
            **{code: "retry" for code in _RETRY_CODES},
        }
        expected.update(kind[body])
        expected[403] = "guard" if body == "html" else "skip"
        expected[200] = "guard" if body == "html" else "SUCCESS"
        for status_code, outcome in expected.items():
            actual = _outcome(handler.interpret_response(_response(status_code, body == "html")))
            if actual != outcome:
                mismatches.append(f"{body} {status_code}: expected {outcome}, got {actual}")

    assert not mismatches, mismatches


_SCOPE_MISMATCH = {"success": False, "error": "Scope and URL mismatch", "errorCode": 403}


@pytest.mark.parametrize("stream", list(_STREAM_KINDS))
def test_every_per_stream_handler_fails_a_missing_oauth_scope_before_its_403_skip(stream) -> None:
    # A missing app scope is a setup problem, so the per-record 403 skips must not swallow it.
    response = _response(403, html=False)
    response._content = json.dumps(_SCOPE_MISMATCH).encode()

    resolution = _per_stream_handler(stream).interpret_response(response)

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert "lacks the scope" in resolution.error_message


@pytest.mark.parametrize("stream", ["deals", "deal_products", "deal_flow"])
def test_missing_oauth_scope_fails_the_sync_instead_of_reading_empty(stream) -> None:
    with HttpMocker() as http_mocker:
        response = HttpResponse(json.dumps(_SCOPE_MISMATCH), 403)
        if stream == "deals":
            http_mocker.get(deals_request(), response)
        else:
            _mock_gated_stream(http_mocker, stream, response)

        output = read_stream(stream, expecting_exception=True)

    assert output.records == []
    error = _error_trace(output)
    assert error.failure_type == FailureType.config_error
    assert "lacks the scope" in error.message


def _base_error_handler():
    from conftest import _YAML_FILE_PATH

    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, manifest["definitions"]["base_error_handler"], config={})


@pytest.mark.parametrize("stream", ["<base>"] + list(_STREAM_KINDS))
def test_every_handler_refreshes_an_oauth_401_and_fails_a_token_401(stream) -> None:
    handler = _base_error_handler() if stream == "<base>" else _per_stream_handler(stream)
    for url, action in (
        ("https://acme.pipedrive.com/api/v1/example", ResponseAction.REFRESH_TOKEN_THEN_RETRY),
        ("https://api.pipedrive.com/v1/example", ResponseAction.FAIL),
    ):
        response = _response(401, html=False)
        response._content = json.dumps({"success": False, "error": "unauthorized access", "errorCode": 401}).encode()
        response.request = requests.Request("GET", url).prepare()
        response.url = url

        assert handler.interpret_response(response).response_action == action, url
