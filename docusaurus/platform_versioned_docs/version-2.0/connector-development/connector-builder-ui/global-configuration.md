# Global Configuration

Global Configuration settings in the Connector Builder UI allow you to define connector-wide behaviors that apply across all streams. These settings control how your connector validates connections, manages request concurrency, and handles API rate limiting.

## Check

The Check configuration determines which streams are used to validate that your connector can successfully connect to the data source. This validation runs when users test their connection or when Airbyte verifies the connector is working properly.

### Streams to check

Use this option when you want to validate the connection using specific, known stream names. This is the most common approach for connectors with well-defined, static streams.

In the UI, you can specify one or more stream names that should be used for connection validation. The connector will attempt to read from these streams to verify the connection is working.

**When to use:** When your connector has predictable stream names that are always available, such as `users`, `accounts`, or `organizations`.

### Dynamic streams to check

Use this option when your connector generates streams dynamically based on the user's configuration or the data source's current state. Instead of specifying exact stream names, you define how many streams to check.

In the UI, you can specify:
- **Dynamic stream name**: The pattern or base name for dynamically generated streams
- **Stream count**: How many of the dynamic streams to use for validation

**When to use:** When your connector creates streams based on user input (like custom report names) or when the available streams change based on the data source's configuration.

## Concurrency Level

Concurrency Level controls how many simultaneous requests your connector can make to the API. This helps optimize performance while respecting the API's capacity limits.

### Default Concurrency

The Default Concurrency setting determines the baseline number of concurrent requests your connector will make. This can be configured as:

- **Integer value**: A fixed number of concurrent requests (e.g., `5` for 5 simultaneous requests)
- **String value**: A reference to a user configuration field (e.g., `"{{ config['concurrency'] }}"` to let users control concurrency)

### Max Concurrency

Max Concurrency acts as a safety limit when Default Concurrency is derived from user configuration. This prevents users from setting unreasonably high concurrency levels that could overwhelm the API or cause performance issues.

**Example:** If Default Concurrency is set to `"{{ config['max_workers'] }}"` and Max Concurrency is set to `10`, the connector will use the user's configured value but never exceed 10 concurrent requests.

## HTTP API Budget

HTTP API Budget provides sophisticated rate limiting to ensure your connector respects the API's usage limits and avoids being throttled or blocked. The system supports three different rate limiting policies that can be combined to match your API's specific requirements.

### Rate Limit Policies

#### Fixed Window Call Rate Policy

This policy allows a fixed number of calls within specific time windows (e.g., 1000 calls per hour). When the time window ends, the limit resets completely.

**Use case:** APIs that reset their rate limits at fixed intervals, such as hourly or daily limits.

**Example:** An API that allows 1000 requests per hour, resetting at the top of each hour.

#### Moving Window Call Rate Policy

This policy tracks calls within a sliding time window (e.g., 100 calls per minute). Unlike fixed windows, this continuously tracks the last N minutes/seconds of activity.

**Use case:** APIs that enforce rate limits based on recent activity rather than fixed time periods.

**Example:** An API that allows 100 requests in any 60-second period, continuously monitoring the last minute of activity.

#### Unlimited Window Call Rate Policy

This policy removes rate limiting for specific types of requests, allowing unlimited calls that match certain criteria.

**Use case:** APIs that have different limits for different endpoints, where some endpoints (like metadata or health checks) are unrestricted.

**Example:** An API that limits most endpoints but allows unlimited access to `/health` or `/metadata` endpoints.

### Rate Limit Headers

The HTTP API Budget can automatically extract rate limit information from API response headers to optimize request timing:

#### Rate Limit Reset Header

Specifies which HTTP response header contains the timestamp when the rate limit will reset. Common examples include `X-RateLimit-Reset` or `RateLimit-Reset`.

#### Rate Limit Remaining Header

Specifies which HTTP response header contains the number of remaining requests allowed in the current period. Common examples include `X-RateLimit-Remaining` or `RateLimit-Remaining`.

### Status Codes for Rate Limit Hit

Configure which HTTP status codes indicate that a rate limit has been exceeded. The most common is `429 Too Many Requests`, but some APIs use other codes like `420` or `503`.

When these status codes are encountered, the connector will automatically pause requests and retry according to the rate limiting policy.
