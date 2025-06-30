# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""A mitm-proxy intercept script.

This proves whether the proxy is working by intercepting a specific URL
and modifying the response to return a different CSV.

Usage:
```bash
# First launch the proxy sever:
uvx --from=mitmproxy mitmdump --listen-port 8080 -s integration_tests/proxy_intercept_script.py

# If the secrets file, doesn't exist, create it and open it in an editor to provide the proxy CA cert:
cp integration_tests/proxy_test_config.json.template secrets/proxy_test_config.json
code secrets/proxy_test_config.json

# Now launch the connector:
poetry run python main.py discover --config secrets/proxy_test_config.json
"""

from mitmproxy import http


def response(flow: http.HTTPFlow) -> None:
    """Intercept ALL httpbin requests and return modified base64 CSV data."""
    if "httpbin.org" in flow.request.pretty_host:
        modified_csv = "intercepted_column,proxy_status\nproxy,INTERCEPTED\ntest,SUCCESS\nverification,CONFIRMED"
        flow.response.text = modified_csv
        flow.response.headers["content-type"] = "text/csv"
        flow.response.status_code = 200

        print("🎯 PROXY INTERCEPTED REQUEST!")
        print(f"   URL: {flow.request.pretty_url}")
        print(f"   Method: {flow.request.method}")
        print(f"   User-Agent: {flow.request.headers.get('User-Agent', 'Not set')}")
        print(f"   Modified response: {modified_csv}")
        print("=" * 60)


def request(flow: http.HTTPFlow) -> None:
    """Log ALL requests to prove proxy is receiving traffic."""
    print(f"📡 PROXY RECEIVED REQUEST: {flow.request.method} {flow.request.pretty_url}")
    print(f"   Headers: {dict(flow.request.headers)}")
