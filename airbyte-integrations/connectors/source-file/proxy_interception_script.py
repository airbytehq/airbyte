from mitmproxy import http
import base64


def response(flow: http.HTTPFlow) -> None:
    """Intercept ALL requests and return modified base64 CSV data"""
    if "httpbin.org" in flow.request.pretty_host:
        modified_csv = "intercepted_column,proxy_status\nproxy,INTERCEPTED\ntest,SUCCESS\nverification,CONFIRMED"

        if "/base64/" in flow.request.path:
            modified_b64 = base64.b64encode(modified_csv.encode()).decode()
            flow.response.text = modified_b64
        else:
            flow.response.text = modified_csv

        flow.response.headers["content-type"] = "text/plain"
        flow.response.status_code = 200

        print("🎯 PROXY INTERCEPTED REQUEST!")
        print(f"   URL: {flow.request.pretty_url}")
        print(f"   Method: {flow.request.method}")
        print(f"   User-Agent: {flow.request.headers.get('User-Agent', 'Not set')}")
        print(f"   Modified response: {modified_csv}")
        print("=" * 60)


def request(flow: http.HTTPFlow) -> None:
    """Log ALL requests to prove proxy is receiving traffic"""
    print(f"📡 PROXY RECEIVED REQUEST: {flow.request.method} {flow.request.pretty_url}")
    print(f"   Headers: {dict(flow.request.headers)}")
