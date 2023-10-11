from airbyte_cdk.sources.streams.call_rate import HttpRequestMatcher, APIBudget, CallRatePolicy, Rate, Duration

from requests import Request


def test_http_mapping():
    api_budget = APIBudget()
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/users", method="GET"),
        policy=CallRatePolicy(
            rates=[
                Rate(10, Duration.MINUTE),
                Rate(100, Duration.HOUR),
            ],
        ),
    )
    api_budget.add_policy(
        request_matcher=HttpRequestMatcher(url="/groups", method="POST"),
        policy=CallRatePolicy(
            rates=[
                Rate(1, Duration.SECOND),
            ],
        ),
    )

    assert api_budget.acquire_call(Request("POST", url="/unmatched_endpoint")), "unrestricted call"
    assert api_budget.acquire_call(Request("GET", url="/users")), "first call"
    assert api_budget.acquire_call(Request("GET", url="/users")), "second call"
    for i in range(8):
        assert api_budget.acquire_call(Request("GET", url="/users")), f"{i + 3} call"
    assert not api_budget.acquire_call(Request("GET", url="/users")), "call over limit"

    assert api_budget.acquire_call(Request("POST", url="/groups")), "doesn't affect other policies"
    assert api_budget.acquire_call(Request("POST", url="/list")), "unrestricted call"
