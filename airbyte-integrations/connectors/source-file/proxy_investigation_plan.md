# HTTP Proxy Investigation Plan for Source-File Connector

## Background

The source-file connector has been enhanced with HTTP proxy URL and custom CA certificate support in PR #61521. However, initial testing suggests that proxy settings may be completely ignored by the underlying smart_open library, which appears to fall back to direct connections when proxy configuration is present.

## Current Implementation Status

- ✅ **Proxy configuration parsing**: Correctly implemented in spec.json and client.py
- ✅ **Transport params**: Proxy settings properly passed to smart_open via transport_params
- ✅ **All tests passing**: 63/63 connector tests pass including new proxy tests
- ❓ **Actual proxy usage**: Unclear if smart_open actually uses the proxy or falls back to direct connections

## Investigation Objective

Definitively determine whether the HTTP proxy configuration is:
1. **Working as intended**: Requests flow through the configured proxy
2. **Being bypassed**: smart_open ignores proxy settings and uses direct connections
3. **Conditionally working**: Proxy works in some scenarios but not others

## Repro Setup Instructions

### Step 1: Create Test Configuration

Create `integration_tests/proxy_test_config.json`:
```json
{
  "dataset_name": "proxy_investigation_test",
  "format": "csv",
  "url": "https://httpbin.org/base64/a2V5LHZhbHVlCmZvbyxiYXIKYW5zd2VyLDQyCnF1ZXN0aW9uLHdobyBrbm93cw==",
  "provider": {
    "storage": "HTTPS",
    "proxy_url": "http://localhost:8080"
  }
}
```

**Note**: This URL decodes to CSV with columns: `key,value` and rows: `foo,bar`, `answer,42`, `question,who knows`

### Step 2: Create Mitmproxy Interception Script

Create `proxy_interception_script.py`:
```python
from mitmproxy import http
import base64

def response(flow: http.HTTPFlow) -> None:
    """Intercept ALL requests and return modified base64 CSV data"""
    if "httpbin.org" in flow.request.pretty_host:
        # Create completely different CSV to prove interception
        modified_csv = "intercepted_column,proxy_status\nproxy,INTERCEPTED\ntest,SUCCESS\nverification,CONFIRMED"
        
        # Return as base64 if original was base64, otherwise return directly
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
```

### Step 3: Start Mitmproxy

```bash
uvx --from=mitmproxy mitmdump --listen-port 8080 -s proxy_interception_script.py
```

**Expected output**: Mitmproxy should start and show "Proxy server listening at http://*:8080"

### Step 4: Run Discovery with Proxy Configuration

```bash
cd airbyte-integrations/connectors/source-file
poetry run python main.py discover --config integration_tests/proxy_test_config.json
```

### Step 5: Analyze Results

**If proxy is working correctly:**
- Mitmproxy logs should show: "📡 PROXY RECEIVED REQUEST" and "🎯 PROXY INTERCEPTED REQUEST!"
- Discovery output should show schema with columns: `intercepted_column`, `proxy_status`
- Data should include rows: `proxy,INTERCEPTED`, `test,SUCCESS`, `verification,CONFIRMED`

**If proxy is being bypassed:**
- Mitmproxy logs should show NO requests
- Discovery output should show original schema with columns: `key`, `value`
- Data should include original rows: `foo,bar`, `answer,42`, `question,who knows`

## Additional Investigation Points

### 1. Smart_open Library Behavior

Investigate smart_open's proxy handling:
- Check smart_open version: `poetry show smart-open`
- Review smart_open documentation for proxy support limitations
- Test with different proxy configurations (HTTP vs HTTPS proxy URLs)

### 2. Transport Params Verification

Add debug logging to client.py to verify transport_params:
```python
logger.info(f"Smart_open transport_params: {transport_params}")
logger.info(f"Smart_open args: {self.args}")
```

### 3. Alternative Proxy Testing

Test with different proxy configurations:
- HTTP proxy for HTTPS URLs: `"proxy_url": "http://localhost:8080"`
- HTTPS proxy for HTTPS URLs: `"proxy_url": "https://localhost:8080"`
- Authentication proxy: `"proxy_url": "http://user:pass@localhost:8080"`

### 4. Network-Level Verification

Use network monitoring to verify traffic flow:
```bash
# Monitor network connections
sudo netstat -tulpn | grep :8080

# Monitor HTTP traffic
sudo tcpdump -i lo port 8080
```

## Expected Outcomes

### Scenario A: Proxy Working
- Mitmproxy receives and logs all requests
- Discovery returns intercepted CSV data with modified columns
- Network monitoring shows traffic to localhost:8080

### Scenario B: Proxy Bypassed
- Mitmproxy receives NO requests
- Discovery returns original CSV data
- Network monitoring shows direct connections to httpbin.org

### Scenario C: Conditional Proxy Usage
- Some requests go through proxy, others don't
- Mixed results in discovery output
- Partial traffic to localhost:8080

## Root Cause Investigation

If proxy is being bypassed, investigate:

1. **Smart_open fallback behavior**: Does smart_open silently fall back to direct connections?
2. **Transport_params format**: Are proxy settings in the correct format for smart_open?
3. **SSL/TLS handling**: Does HTTPS URL + HTTP proxy cause issues?
4. **Library version compatibility**: Is the smart_open version compatible with proxy settings?

## Potential Solutions

Based on investigation results:

1. **If smart_open doesn't support proxies**: Switch to requests library directly
2. **If format is wrong**: Adjust transport_params structure
3. **If conditional failure**: Identify and fix specific failure conditions
4. **If library limitation**: Document limitation and consider alternative approaches

## Files to Examine

- `airbyte-integrations/connectors/source-file/source_file/client.py` (lines 152-158)
- `airbyte-integrations/connectors/source-file/source_file/spec.json` (HTTPS provider config)
- `airbyte-integrations/connectors/source-file/pyproject.toml` (smart_open version)

## Success Criteria

This investigation is complete when:
1. ✅ Definitive proof of whether proxy is working or bypassed
2. ✅ Root cause identified if proxy is not working
3. ✅ Recommended solution documented
4. ✅ Test cases created to verify any fixes

## Current PR Status

- **PR #61521**: https://github.com/airbytehq/airbyte/pull/61521
- **Branch**: `devin/1749618047-add-http-proxy-support`
- **Status**: All CI checks passing except Vercel deployment
- **Implementation**: Complete but proxy functionality unverified

This investigation will determine if additional changes are needed to make the proxy functionality actually work as intended.
