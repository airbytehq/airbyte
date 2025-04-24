# Rate limiting (API Budget)

In order to prevent sending too many requests to the API in a short period of time, you can configure an API Budget. This budget determines the maximum number of calls that can be made within a specified time interval (or intervals). This mechanism is particularly useful for respecting third-party API rate limits and avoiding potential throttling or denial of service.

When using an **HTTPAPIBudget**, rate limit updates can be automatically extracted from HTTP response headers such as _remaining calls_ or _time-to-reset_ values.

## Schema

```yaml
HTTPAPIBudget:
  type: object
  title: HTTP API Budget
  description: >
    An HTTP-specific API budget that extends APIBudget by updating rate limiting information based
    on HTTP response headers. It extracts available calls and the next reset timestamp from the HTTP responses.
  required:
    - type
    - policies
  properties:
    type:
      type: string
      enum: [HTTPAPIBudget]
    policies:
      type: array
      description: List of call rate policies that define how many calls are allowed.
      items:
        anyOf:
          - "$ref": "#/definitions/FixedWindowCallRatePolicy"
          - "$ref": "#/definitions/MovingWindowCallRatePolicy"
          - "$ref": "#/definitions/UnlimitedCallRatePolicy"
    ratelimit_reset_header:
      type: string
      default: "ratelimit-reset"
      description: The HTTP response header name that indicates when the rate limit resets.
    ratelimit_remaining_header:
      type: string
      default: "ratelimit-remaining"
      description: The HTTP response header name that indicates the number of remaining allowed calls.
    status_codes_for_ratelimit_hit:
      type: array
      default: [429]
      items:
        type: integer
      description: List of HTTP status codes that indicate a rate limit has been hit.
  additionalProperties: true
```

An `HTTPAPIBudget` may contain one or more rate policies. These policies define how rate limits should be enforced.

## Example usage
```yaml
api_budget:
  type: "HTTPAPIBudget"
  ratelimit_reset_header: "X-RateLimit-Reset"
  ratelimit_remaining_header: "X-RateLimit-Remaining"
  status_codes_for_ratelimit_hit: [ 429 ]
  policies:
    - type: "UnlimitedCallRatePolicy"
      matchers: []
    - type: "FixedWindowCallRatePolicy"
      period: "PT1H"
      call_limit: 1000
      matchers:
        - method: "GET"
          url_base: "https://api.example.com"
          url_path_pattern: "^/users"
    - type: "MovingWindowCallRatePolicy"
      rates:
        - limit: 100
          interval: "PT1M"
      matchers:
        - method: "POST"
          url_base: "https://api.example.com"
          url_path_pattern: "^/users"
```
Above, we define:

1. **UnlimitedCallRatePolicy**: A policy with no limit on requests.
2. **FixedWindowCallRatePolicy**: Allows a set number of calls within a fixed time window (in the example, 1000 calls per 1 hour).
3. **MovingWindowCallRatePolicy**: Uses a moving time window to track how many calls were made in the last interval. In the example, up to 100 calls per 1 minute for `POST /users`.


## Rate Policies
### Unlimited call rate policy
Use this policy if you want to allow unlimited calls for a subset of requests.
For instance, the policy below will not limit requests that match its `matchers`:

```yaml
UnlimitedCallRatePolicy:
  type: object
  title: Unlimited Call Rate Policy
  description: A policy that allows unlimited calls for specific requests.
  required:
    - type
    - matchers
  properties:
    type:
      type: string
      enum: [UnlimitedCallRatePolicy]
    matchers:
      type: array
      items:
        "$ref": "#/definitions/HttpRequestRegexMatcher"
```

#### Example
```yaml
api_budget:
  type: "HTTPAPIBudget"
  policies:
    - type: "UnlimitedCallRatePolicy"
      # For any GET request on https://api.example.com/sandbox
      matchers:
        - method: "GET"
          url_base: "https://api.example.com"
          url_path_pattern: "^/sandbox"
```
Here, any request matching the above matcher is not rate-limited.

### Fixed Window Call Rate Policy
This policy allows **n** calls per specified interval (for example, 1000 calls per hour). After the time window ends (the “fixed window”), it resets, and you can make new calls.

```yaml
FixedWindowCallRatePolicy:
  type: object
  title: Fixed Window Call Rate Policy
  description: A policy that allows a fixed number of calls within a specific time window.
  required:
    - type
    - period
    - call_limit
    - matchers
  properties:
    type:
      type: string
      enum: [FixedWindowCallRatePolicy]
    period:
      type: string
      format: duration
    call_limit:
      type: integer
    matchers:
      type: array
      items:
        "$ref": "#/definitions/HttpRequestRegexMatcher"
    additionalProperties: true
```
- **period**: In ISO 8601 duration format (e.g. `PT1H` for 1 hour, `PT15M` for 15 minutes).
- **call_limit**: Maximum allowed calls within that period.
- **matchers**: A list of request matchers (by HTTP method, URL path, etc.) that this policy applies to.

#### Example
```yaml
api_budget:
 type: "HTTPAPIBudget"
 policies:
   - type: "FixedWindowCallRatePolicy"
     period: "PT1H"
     call_limit: 1000
     matchers:
       - method: "GET"
         url_base: "https://api.example.com"
         url_path_pattern: "^/users"
```

### Moving Window Call Rate Policy
This policy allows a certain number of calls in a “sliding” or “moving” window, using timestamps for each call. For example, 100 requests allowed within the last 60 seconds.

```yaml
MovingWindowCallRatePolicy:
  type: object
  title: Moving Window Call Rate Policy
  description: A policy that allows a fixed number of calls within a moving time window.
  required:
    - type
    - rates
    - matchers
  properties:
    type:
      type: string
      enum: [MovingWindowCallRatePolicy]
    rates:
      type: array
      items:
        "$ref": "#/definitions/Rate"
    matchers:
      type: array
      items:
        "$ref": "#/definitions/HttpRequestRegexMatcher"
    additionalProperties: true
```

- **rates**: A list of `Rate` objects, each specifying a `limit` and `interval`.
- **interval**: An ISO 8601 duration (e.g., `"PT1M"` is 1 minute).
- **limit**: Number of calls allowed within that interval.

#### Example
```yaml
api_budget:
  type: "HTTPAPIBudget"
  policies:
    - type: "MovingWindowCallRatePolicy"
      rates:
        - limit: 100
          interval: "PT1M"
      matchers:
        - method: "GET"
          url_base: "https://api.example.com"
          url_path_pattern: "^/orders"
```
In this example, at most 100 requests to `GET /orders` can be made in any rolling 1-minute period.

## Matching requests with matchers
Each policy has a `matchers` array of objects defining which requests it applies to. The schema for each matcher:

```yaml
HttpRequestRegexMatcher:
  type: object
  properties:
    method:
      type: string
      description: The HTTP method (e.g. GET, POST).
    url_base:
      type: string
      description: The base URL to match (e.g. "https://api.example.com" without trailing slash).
    url_path_pattern:
      type: string
      description: A regular expression to match the path portion.
    params:
      type: object
      additionalProperties: true
    headers:
      type: object
      additionalProperties: true
  additionalProperties: true
```
- **method**: Matches if the request method equals the one in the matcher (case-insensitive).
- **url_base**: Matches the scheme + host portion (no trailing slash).
- **url_path_pattern**: Regex is tested against the request path.
- **params**: The query parameters must match.
- **headers**: The headers must match.
A request is rate-limited by the first policy whose matchers pass. If no policy matches, then the request will be allowed if you have not defined a default/other policy that catches everything else.

## Putting it all together
You may define multiple policies for different endpoints. For example:

```yaml
api_budget:
  type: "HTTPAPIBudget"
  # Use standard rate limit headers from your API
  ratelimit_reset_header: "X-RateLimit-Reset"
  ratelimit_remaining_header: "X-RateLimit-Remaining"
  status_codes_for_ratelimit_hit: [429, 420]

  policies:
    # Policy 1: Unlimited
    - type: "UnlimitedCallRatePolicy"
      matchers:
        - url_base: "https://api.example.com"
          method: "GET"
          url_path_pattern: "^/sandbox"

    # Policy 2: 1000 calls per hour
    - type: "FixedWindowCallRatePolicy"
      period: "PT1H"
      call_limit: 1000
      matchers:
        - method: "GET"
          url_base: "https://api.example.com"
          url_path_pattern: "^/users"

    # Policy 3: 500 calls per hour
    - type: "FixedWindowCallRatePolicy"
      period: "PT1H"
      call_limit: 500
      matchers:
        - method: "POST"
          url_base: "https://api.example.com"
          url_path_pattern: "^/orders"

    # Policy 4: 20 calls every 5 minutes (moving window).
    - type: "MovingWindowCallRatePolicy"
      rates:
        - limit: 20
          interval: "PT5M"
      matchers:
        - url_base: "https://api.example.com"
          url_path_pattern: "^/internal"
```
1. The request attempts to match the first policy (unlimited on `GET /sandbox`). If it matches, it’s unlimited. 
2. Otherwise, it checks the second policy (1000/hour for `GET /users`), etc. 
3. If still no match, it is not rate-limited by these defined policies (unless you add a “catch-all” policy).
