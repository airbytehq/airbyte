---
id: airbyte_agent_sdk-auth_strategies
title: airbyte_agent_sdk.auth_strategies
---

Module airbyte_agent_sdk.auth_strategies
========================================
Authentication strategy pattern implementation for HTTP client.

Functions
---------

<a id="extract_secret_value"></a>

`extract_secret_value(value: SecretStr | str | None) ‑> str`
:   Extract the actual value from SecretStr or return plain string.
    
    This utility function handles the common pattern of extracting secret values
    that can be either SecretStr (wrapped) or plain str values.
    
    Note:
        Accepts None and returns empty string for convenience when accessing
        optional TypedDict fields. This avoids repetitive None checks in callers
        when building headers/bodies where missing optional fields should use "".
    
    Args:
        value: A SecretStr, plain string, or None
    
    Returns:
        The unwrapped string value, or empty string if None
    
    Examples:
        >>> extract_secret_value(SecretStr("my_secret"))
        'my_secret'
        >>> extract_secret_value("plain_value")
        'plain_value'
        >>> extract_secret_value(None)
        ''

Classes
-------

<a id="APIKeyAuthConfig"></a>

`APIKeyAuthConfig(*args, **kwargs)`
:   Configuration for API key authentication.
    
    Attributes:
        header: Header name to use (default: "Authorization")
        prefix: Prefix for the header value (default: "Bearer")

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `header: str`
    :   The type of the None singleton.

    `prefix: str`
    :   The type of the None singleton.

<a id="APIKeyAuthSecrets"></a>

`APIKeyAuthSecrets(*args, **kwargs)`
:   Required secrets for API key authentication.
    
    Attributes:
        api_key: The API key credential

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `api_key: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

<a id="APIKeyAuthStrategy"></a>

`APIKeyAuthStrategy()`
:   Strategy for API key authentication.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.auth_strategies.AuthStrategy
    * abc.ABC

    ### Methods

    `inject_auth(self, headers: dict[str, str], config: APIKeyAuthConfig, secrets: APIKeyAuthSecrets) ‑> dict[str, str]`
    :   Inject API key into headers.
        
        Creates a copy of the headers dict with the API key added.
        The original headers dict is not modified.
        
        Args:
            headers: Existing request headers (will not be modified)
            config: API key authentication configuration
            secrets: API key credentials
        
        Returns:
            New headers dict with API key authentication injected

    `validate_credentials(self, secrets: APIKeyAuthSecrets) ‑> None`
    :   Validate API key is present.
        
        Args:
            secrets: API key credentials to validate

<a id="AuthStrategy"></a>

`AuthStrategy()`
:   Abstract base class for authentication strategies.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_agent_sdk.auth_strategies.APIKeyAuthStrategy
    * airbyte_agent_sdk.auth_strategies.BasicAuthStrategy
    * airbyte_agent_sdk.auth_strategies.BearerAuthStrategy
    * airbyte_agent_sdk.auth_strategies.OAuth2AuthStrategy

    ### Methods

    `ensure_credentials(self, config: dict[str, Any], secrets: dict[str, Any], config_values: dict[str, str] | None = None, http_client: httpx.AsyncClient | None = None) ‑> airbyte_agent_sdk.auth_strategies.TokenRefreshResult | None`
    :   Ensure credentials are ready for authentication.
        
        This method is called before the first API request to allow
        strategies to proactively obtain credentials (e.g., OAuth2 token refresh
        when starting with only a refresh_token).
        
        Args:
            config: Authentication configuration from AuthConfig.config
            secrets: Secret credentials dictionary (may be updated by caller)
            config_values: Non-secret configuration values for template substitution
            http_client: Optional httpx.AsyncClient for making requests
        
        Returns:
            TokenRefreshResult with new/updated credentials if changes were made, None otherwise.
            The tokens dict should be merged into the secrets dict by the caller.
        
        Note:
            Default implementation returns None (no initialization needed).
            Strategies like OAuth2 can override this for proactive token refresh.

    `handle_auth_error(self, status_code: int, config: dict[str, Any], secrets: dict[str, Any], config_values: dict[str, str] | None = None, http_client: httpx.AsyncClient | None = None) ‑> airbyte_agent_sdk.auth_strategies.TokenRefreshResult | None`
    :   Handle authentication error and attempt recovery (e.g., token refresh).
        
        This method is called by HTTPClient when an authentication error occurs.
        Strategies that support credential refresh (like OAuth2) can override this
        to implement their refresh logic.
        
        Args:
            status_code: HTTP status code of the auth error (e.g., 401, 403)
            config: Authentication configuration from AuthConfig.config
            secrets: Secret credentials dictionary (may be updated)
            config_values: Non-secret configuration values (e.g., \{"subdomain": "mycompany"\})
                Used for template variable substitution in refresh URLs.
            http_client: Optional httpx.AsyncClient for making refresh requests.
                If provided, will be reused; otherwise a new client is created.
        
        Returns:
            TokenRefreshResult with new credentials if refresh successful, None otherwise.
            The tokens dict will be merged into the secrets dict by the caller.
        
        Note:
            Default implementation returns None (no refresh capability).
            Strategies with refresh capability should override this method.

    `inject_auth(self, headers: dict[str, str], config: dict[str, Any], secrets: dict[str, SecretStr | str]) ‑> dict[str, str]`
    :   Inject authentication credentials into request headers.
        
        This method creates a copy of the headers dict and adds authentication.
        The original headers dict is not modified.
        
        Args:
            headers: Existing request headers (will not be modified)
            config: Authentication configuration from AuthConfig.config
            secrets: Secret credentials dictionary (SecretStr or plain str values)
        
        Returns:
            New headers dictionary with authentication injected (original unchanged)
        
        Raises:
            AuthenticationError: If required credentials are missing

    `validate_credentials(self, secrets: dict[str, SecretStr | str]) ‑> None`
    :   Validate that required credentials are present.
        
        Args:
            secrets: Secret credentials dictionary with SecretStr values
        
        Raises:
            AuthenticationError: If required credentials are missing

<a id="AuthStrategyFactory"></a>

`AuthStrategyFactory()`
:   Factory for creating authentication strategies.

    ### Static methods

    `get_strategy(auth_type: AuthType) ‑> airbyte_agent_sdk.auth_strategies.AuthStrategy`
    :   Get authentication strategy for the given auth type.
        
        Args:
            auth_type: Authentication type from AuthConfig
        
        Returns:
            Appropriate AuthStrategy instance
        
        Raises:
            AuthenticationError: If auth type is not implemented

    `register_strategy(auth_type: AuthType, strategy: AuthStrategy) ‑> None`
    :   Register a custom authentication strategy.
        
        Args:
            auth_type: Authentication type to register
            strategy: Strategy instance to use for this auth type

<a id="BasicAuthSecrets"></a>

`BasicAuthSecrets(*args, **kwargs)`
:   Required secrets for HTTP Basic authentication.
    
    Attributes:
        username: The username credential
        password: The password credential

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `password: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

    `username: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

<a id="BasicAuthStrategy"></a>

`BasicAuthStrategy()`
:   Strategy for HTTP Basic authentication.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.auth_strategies.AuthStrategy
    * abc.ABC

    ### Methods

    `inject_auth(self, headers: dict[str, str], config: dict[str, Any], secrets: BasicAuthSecrets) ‑> dict[str, str]`
    :   Inject Basic auth credentials into Authorization header.
        
        Creates a copy of the headers dict with Basic auth added.
        The original headers dict is not modified.
        
        Args:
            headers: Existing request headers (will not be modified)
            config: Basic authentication configuration (unused)
            secrets: Basic auth credentials
        
        Returns:
            New headers dict with Authorization header added

    `validate_credentials(self, secrets: BasicAuthSecrets) ‑> None`
    :   Validate username and password are present.
        
        Args:
            secrets: Basic auth credentials to validate

<a id="BearerAuthConfig"></a>

`BearerAuthConfig(*args, **kwargs)`
:   Configuration for Bearer token authentication.
    
    Attributes:
        header: Header name to use (default: "Authorization")
        prefix: Prefix for the header value (default: "Bearer")

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `header: str`
    :   The type of the None singleton.

    `prefix: str`
    :   The type of the None singleton.

<a id="BearerAuthSecrets"></a>

`BearerAuthSecrets(*args, **kwargs)`
:   Required secrets for Bearer authentication.
    
    Attributes:
        token: The bearer token (can be SecretStr or plain str, will be converted as needed)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `token: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

<a id="BearerAuthStrategy"></a>

`BearerAuthStrategy()`
:   Strategy for Bearer token authentication.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.auth_strategies.AuthStrategy
    * abc.ABC

    ### Methods

    `inject_auth(self, headers: dict[str, str], config: BearerAuthConfig, secrets: BearerAuthSecrets) ‑> dict[str, str]`
    :   Inject Bearer token into headers.
        
        Creates a copy of the headers dict with the Bearer token added.
        The original headers dict is not modified.
        
        Args:
            headers: Existing request headers (will not be modified)
            config: Bearer authentication configuration
            secrets: Bearer token credentials
        
        Returns:
            New headers dict with Bearer token authentication injected

    `validate_credentials(self, secrets: BearerAuthSecrets) ‑> None`
    :   Validate token is present.
        
        Args:
            secrets: Bearer token credentials to validate

<a id="OAuth2AuthConfig"></a>

`OAuth2AuthConfig(*args, **kwargs)`
:   Configuration for OAuth 2.0 authentication.
    
    All fields are optional with sensible defaults. Used to customize OAuth2
    authentication behavior for different APIs.
    
    Attributes:
        header: Header name to use (default: "Authorization")
            Example: "X-OAuth-Token" for custom header names
    
        prefix: Prefix for the header value (default: "Bearer")
            Example: "Token" for APIs that use "Token \{access_token\}"
    
        refresh_url: Token refresh endpoint URL (supports Jinja2 \{\{templates\}\})
            Required for token refresh functionality.
            Example: "https://\{\{subdomain\}\}.zendesk.com/oauth/tokens"
            If template variables are used but not provided, they render as empty strings.
    
        auth_style: How to send client credentials during token refresh
            - "basic": client_id:client_secret in Basic Auth header (RFC 6749 compliant)
            - "body": credentials in request body (default, widely supported)
            - "none": no client credentials sent (public clients)
            Default: "body"
    
        body_format: Request body encoding for token refresh
            - "form": application/x-www-form-urlencoded (default, RFC 6749 standard)
            - "json": application/json (some APIs prefer this)
            Default: "form"
    
        subdomain: Template variable for multi-tenant APIs (e.g., Zendesk)
            Used in refresh_url templates like "https://\{\{subdomain\}\}.example.com"
            If not provided and used in template, renders as empty string.
    
            Note: Any config key can be used as a template variable in refresh_url.
            Common patterns: subdomain (Zendesk), shop (Shopify), region (AWS-style APIs).
    
        additional_headers: Extra headers to inject alongside the OAuth2 Bearer token.
            Useful for APIs that require both OAuth and an API key/client ID header.
            Values support Jinja2 \{\{ variable \}\} template syntax to reference secrets.
            Example: \{"Amazon-Advertising-API-ClientId": "\{\{ client_id \}\}"\}
    
    Examples:
        GitHub (simple):
            \{"header": "Authorization", "prefix": "Bearer"\}
    
        Zendesk (with subdomain):
            \{
                "refresh_url": "https://\{\{subdomain\}\}.zendesk.com/oauth/tokens",
                "subdomain": "mycompany",
                "auth_style": "body"
            \}
    
        Custom API (JSON body, basic auth):
            \{
                "refresh_url": "https://api.example.com/token",
                "auth_style": "basic",
                "body_format": "json"
            \}
    
        Amazon Ads (OAuth + additional client ID header):
            \{
                "refresh_url": "https://api.amazon.com/auth/o2/token",
                "additional_headers": \{
                    "Amazon-Advertising-API-ClientId": "\{\{ client_id \}\}"
                \}
            \}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_headers: dict[str, str]`
    :   The type of the None singleton.

    `auth_style: Literal['basic', 'body', 'none']`
    :   The type of the None singleton.

    `body_format: Literal['form', 'json']`
    :   The type of the None singleton.

    `header: str`
    :   The type of the None singleton.

    `prefix: str`
    :   The type of the None singleton.

    `refresh_url: str`
    :   The type of the None singleton.

    `subdomain: str`
    :   The type of the None singleton.

<a id="OAuth2AuthSecrets"></a>

`OAuth2AuthSecrets(*args, **kwargs)`
:   Required secrets for OAuth 2.0 authentication.
    
    Minimum secrets needed to make authenticated requests. The access_token
    is the only required field for basic OAuth2 authentication.
    
    Attributes:
        access_token: The OAuth2 access token (REQUIRED)
            This is the credential used to authenticate API requests.
            Can be either a SecretStr (recommended) or plain string.
    
    Examples:
        Basic usage with string:
            \{"access_token": "gho_abc123xyz..."\}
    
        Secure usage with SecretStr:
            \{"access_token": SecretStr("gho_abc123xyz...")\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_token: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

<a id="OAuth2AuthStrategy"></a>

`OAuth2AuthStrategy()`
:   Strategy for OAuth 2.0 authentication with token refresh support.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.auth_strategies.AuthStrategy
    * abc.ABC

    ### Methods

    `can_refresh(self, secrets: OAuth2RefreshSecrets) ‑> bool`
    :   Check if token refresh is possible.
        
        Args:
            secrets: OAuth2 credentials (including optional refresh fields)
        
        Returns:
            True if refresh_token is available, False otherwise

    `ensure_credentials(self, config: dict[str, Any], secrets: dict[str, Any], config_values: dict[str, str] | None = None, http_client: httpx.AsyncClient | None = None) ‑> airbyte_agent_sdk.auth_strategies.TokenRefreshResult | None`
    :   Proactively refresh OAuth2 tokens if access_token is missing.
        
        Called before the first API request. If access_token is missing
        but refresh credentials are available, attempts to obtain an
        access_token via token refresh.
        
        Args:
            config: OAuth2 authentication configuration
            secrets: OAuth2 credentials (may be missing access_token)
            config_values: Non-secret config values for URL templates
            http_client: Optional httpx.AsyncClient for refresh request (unused)
        
        Returns:
            TokenRefreshResult with new tokens if refresh successful, None otherwise
        
        Raises:
            AuthenticationError: If refresh fails and no access_token available

    `handle_auth_error(self, status_code: int, config: dict[str, Any], secrets: dict[str, Any], config_values: dict[str, str] | None = None, http_client: httpx.AsyncClient | None = None) ‑> airbyte_agent_sdk.auth_strategies.TokenRefreshResult | None`
    :   Handle OAuth2 authentication error by refreshing tokens.
        
        This method is called when a 401 error occurs. It attempts to refresh
        the access_token using the refresh_token if available.
        
        Args:
            status_code: HTTP status code (only 401 triggers refresh)
            config: OAuth2 authentication configuration
            secrets: OAuth2 credentials including refresh_token
            config_values: Non-secret configuration values for template substitution
            http_client: Optional httpx.AsyncClient for making refresh requests
        
        Returns:
            TokenRefreshResult with new tokens if refresh successful, None otherwise.
        
        Note:
            Only attempts refresh on 401 (Unauthorized) errors with valid refresh_token.
            Other status codes (403, etc.) return None immediately.

    `inject_auth(self, headers: dict[str, str], config: OAuth2AuthConfig, secrets: OAuth2AuthSecrets) ‑> dict[str, str]`
    :   Inject OAuth2 access token and additional headers.
        
        Creates a copy of the headers dict with the OAuth2 token added,
        plus any additional headers configured via additional_headers.
        The original headers dict is not modified.
        
        Args:
            headers: Existing request headers (will not be modified)
            config: OAuth2 authentication configuration
            secrets: OAuth2 credentials including access_token
        
        Returns:
            New headers dict with OAuth2 token and additional headers injected
        
        Raises:
            AuthenticationError: If access_token is missing

    `needs_proactive_refresh(self, secrets: dict[str, Any]) ‑> bool`
    :   Check if proactive token refresh is needed.
        
        Returns True if:
        - access_token is missing (None, empty, or not present)
        - refresh_token is present
        
        This indicates "refresh-token-only" mode where we need to obtain
        an access_token before making API requests.
        
        Args:
            secrets: OAuth2 credentials
        
        Returns:
            True if proactive refresh should be attempted, False otherwise

    `validate_credentials(self, secrets: OAuth2AuthSecrets) ‑> None`
    :   Validate OAuth2 credentials are valid for authentication.
        
        Validates that either:
        1. access_token is present, OR
        2. refresh_token is present (for refresh-token-only mode)
        
        Args:
            secrets: OAuth2 credentials to validate
        
        Raises:
            AuthenticationError: If neither access_token nor refresh_token is present

<a id="OAuth2RefreshSecrets"></a>

`OAuth2RefreshSecrets(*args, **kwargs)`
:   Extended OAuth2 secrets including optional refresh-related fields.
    
    Inherits the required access_token from OAuth2AuthSecrets and adds
    optional fields needed for automatic token refresh when access_token expires.
    
    Note on typing:
        This class uses `total=False` which makes all fields defined HERE optional.
        The inherited `access_token` from OAuth2AuthSecrets remains REQUIRED.
        Optional fields may be absent from the dict entirely (checked via `.get()`).
        TypedDict is a static typing construct only - runtime validation uses `.get()`.
    
    Token refresh will be attempted automatically on 401 errors if:
    1. refresh_token is provided
    2. refresh_url is configured in OAuth2AuthConfig
    3. The API returns a 401 Unauthorized response
    
    Attributes:
        refresh_token (optional): Token used to obtain new access_token.
            Required for automatic token refresh functionality.
            Some OAuth2 flows (e.g., client_credentials) don't provide this.
    
        client_id (optional): OAuth2 client ID for refresh requests.
            Required for most token refresh requests.
            How it's sent depends on auth_style config.
    
        client_secret (optional): OAuth2 client secret for refresh requests.
            Required for confidential clients.
            Public clients (mobile apps, SPAs) may not have this.
    
        token_type (optional): Token type, defaults to "Bearer".
            Usually "Bearer" per RFC 6750.
            Some APIs use different types like "Token" or "MAC".
    
    Examples:
        Full refresh capability:
            \{
                "access_token": "eyJhbGc...",
                "refresh_token": "def502...",
                "client_id": "my_client_id",
                "client_secret": SecretStr("my_secret"),
                "token_type": "Bearer"
            \}
    
        Public client (no secret):
            \{
                "access_token": "eyJhbGc...",
                "refresh_token": "def502...",
                "client_id": "mobile_app_id"
            \}
    
        No refresh (access_token only):
            \{
                "access_token": "long_lived_token"
            \}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_token: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

    `client_id: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

    `client_secret: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

    `refresh_token: pydantic.types.SecretStr | str`
    :   The type of the None singleton.

    `token_type: str`
    :   The type of the None singleton.

<a id="OAuth2TokenRefresher"></a>

`OAuth2TokenRefresher(http_client: httpx.AsyncClient | None = None, config_values: dict[str, str] | None = None)`
:   Handles OAuth2 token refresh HTTP requests.
    
    Separated from OAuth2AuthStrategy to maintain single responsibility
    and make testing easier.
    
    Attributes:
        _http_client: Optional httpx.AsyncClient for making HTTP requests.
                      If None, creates a new client for each refresh request.
        _config_values: Non-secret configuration values for template substitution.
    
    Initialize the token refresher.
    
    Args:
        http_client: Optional httpx.AsyncClient instance. If provided,
                    will be used for token refresh requests. If None,
                    a new client will be created for each request.
        config_values: Non-secret configuration values (e.g., \{"subdomain": "mycompany"\})
                      for template variable substitution in refresh URLs.

    ### Class variables

    `MAX_ERROR_RESPONSE_LENGTH`
    :   The type of the None singleton.

    ### Methods

    `refresh_token(self, config: OAuth2AuthConfig, secrets: OAuth2RefreshSecrets) ‑> airbyte_agent_sdk.auth_strategies.TokenRefreshResult`
    :   Refresh the OAuth2 access token using the refresh token.
        
        This method orchestrates the token refresh flow by:
        1. Validating required configuration and secrets
        2. Building the refresh request (URL, headers, body)
        3. Executing the HTTP request
        4. Parsing and validating the response
        
        Args:
            config: OAuth2 configuration with refresh_url and auth_style
            secrets: OAuth2 credentials including refresh_token and client credentials
        
        Returns:
            TokenRefreshResult containing:
                - tokens: dict with access_token, refresh_token (if provided), token_type
                - extracted_values: dict of fields extracted via x-airbyte-token-extract
        
        Raises:
            AuthenticationError: If refresh fails or required fields missing

<a id="TokenRefreshResult"></a>

`TokenRefreshResult(tokens: dict[str, str], extracted_values: dict[str, str] | None = None)`
:   Result of an OAuth2 token refresh operation.
    
    Attributes:
        tokens: Dictionary containing access_token, refresh_token, token_type
        extracted_values: Optional dictionary of values extracted from token response
            for server variable substitution (e.g., instance_url for Salesforce)

    ### Instance variables

    `extracted_values: dict[str, str] | None`
    :   The type of the None singleton.

    `tokens: dict[str, str]`
    :   The type of the None singleton.