---
id: airbyte_agent_sdk-http_client
title: airbyte_agent_sdk.http_client
---

Module airbyte_agent_sdk.http_client
====================================
Async HTTP client with connection pooling, auth injection, metrics, and retry support.

Classes
-------

<a id="HTTPClient"></a>

`HTTPClient(base_url: str, auth_config: AuthConfig, secrets: dict[str, SecretStr | str], config_values: dict[str, str] | None = None, client: HTTPClientProtocol | None = None, logger: Any | None = None, max_connections: int = 100, max_keepalive_connections: int = 20, timeout: float = 30.0, connect_timeout: float | None = None, read_timeout: float | None = None, on_token_refresh: TokenRefreshCallback = None, retry_config: RetryConfig | None = None)`
:   Async HTTP client for making API requests with authentication and connection pooling.
    
    Initialize async HTTP client.
    
    Args:
        base_url: Base URL for API (e.g., https://api.stripe.com)
        auth_config: Authentication configuration from connector.yaml
        secrets: Secret credentials (SecretStr or plain str values)
        config_values: Non-secret configuration values (e.g., \{"subdomain": "mycompany"\})
            Used for server variables and template substitution in OAuth2 refresh URLs.
        client: Optional HTTPClientProtocol implementation. If None, creates HTTPXClient.
        logger: Optional RequestLogger instance for logging requests/responses
        max_connections: Maximum number of concurrent connections
        max_keepalive_connections: Maximum number of keepalive connections
        timeout: Default timeout in seconds (used if connect/read not specified)
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Signature: (new_tokens: dict[str, str]) -> None (sync or async).
            Called when tokens are refreshed. Use to persist updated tokens.
        retry_config: Optional retry configuration for transient errors.
            If None, uses default RetryConfig with sensible defaults.

    ### Static methods

    `create_default(base_url: str, auth_config: AuthConfig, secrets: dict[str, SecretStr | str], logger: Any | None = None, **kwargs: Any) ‑> airbyte_agent_sdk.http_client.HTTPClient`
    :   Create an HTTPClient with default HTTP client (HTTPXClient).
        
        This is a convenience factory method for the common case of using httpx.
        
        Args:
            base_url: Base URL for API (e.g., https://api.stripe.com)
            auth_config: Authentication configuration from connector.yaml
            secrets: Secret credentials (SecretStr or plain str values)
            logger: Optional RequestLogger instance for logging requests/responses
            **kwargs: Additional arguments passed to __init__
        
        Returns:
            Configured HTTPClient instance with HTTPXClient

    ### Methods

    `close(self)`
    :   Close the async HTTP client.

    `request(self, method: str, path: str, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None, *, content: bytes | None = None, stream: bool = False) ‑> tuple[dict[str, typing.Any], dict[str, str]]`
    :   Make an async HTTP request with optional streaming and automatic retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path or full URL
            params: Query parameters
            json: JSON body for POST/PUT
            data: Form-encoded body for POST/PUT (mutually exclusive with json)
            headers: Additional headers
            content: Raw bytes body for multipart/related uploads
            stream: If True, do not eagerly read the body (useful for downloads)
        
        Returns:
            Tuple of (response_data, response_headers):
            - If stream=False: (parsed JSON dict or empty dict, response headers dict)
            - If stream=True: (response object suitable for streaming, response headers dict)
        
        Raises:
            HTTPStatusError: If request fails with 4xx/5xx status after all retries
            AuthenticationError: For 401 or 403 status codes
            RateLimitError: For 429 status codes (after all retries if configured)
            TimeoutError: If request times out (after all retries if configured)
            NetworkError: If network error occurs (after all retries if configured)
            HTTPClientError: For other client errors

<a id="HTTPMetrics"></a>

`HTTPMetrics()`
:   Metrics collector for HTTP requests.
    
    Initialize metrics.

    ### Instance variables

    `avg_duration: float`
    :   Get average request duration.

    ### Methods

    `get_stats(self) ‑> dict[str, typing.Any]`
    :   Get metrics as dictionary.

    `record_request(self, duration: float, status_code: int, success: bool)`
    :   Record a request metric.
        
        Args:
            duration: Request duration in seconds
            status_code: HTTP status code
            success: Whether the request succeeded

    `record_retry(self, delay: float)`
    :   Record a retry attempt.
        
        Args:
            delay: Delay in seconds before the retry