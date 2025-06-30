"""_summary_
A mitm-proxy intercept script.

This proves whether the proxy is working by intercepting a specific URL
and modifying the response to return a different CSV.
"""

from mitmproxy import http


def response(flow: http.HTTPFlow) -> None:
    """Intercept the specific httpbin.org base64 URL."""
    target_path = "/base64/a2V5LHZhbHVlCmZvbyxiYXIKYW5zd2VyLDQyCnF1ZXN0aW9uLHdobyBrbm93cw=="

    print(f"🔍 Checking response for {flow.request.pretty_url}")
    # if "httpbin.org" in flow.request.pretty_host:  # and target_path in flow.request.path:
    # Original CSV would be: key,value\nfoo,bar\nanswer,42\nquestion,who knows
    # Return modified CSV with different headers to prove interception
    intercepted_csv = "intercepted_key,intercepted_value\nproxy,working\ntest,success\ninterception,confirmed"

    flow.response.text = intercepted_csv
    flow.response.headers["content-type"] = "text/csv"
    flow.response.status_code = 200

    print(f"🎯 INTERCEPTED! Modified response for {flow.request.pretty_url}")
    print(f"   Returning: {intercepted_csv}")


def request(flow: http.HTTPFlow) -> None:
    """Log requests to see what's being captured"""
    if "httpbin.org" in flow.request.pretty_host:
        print(f"📡 REQUEST: {flow.request.method} {flow.request.pretty_url}")
