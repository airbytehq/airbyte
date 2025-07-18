# Authentication

Authentication allows the connector to check whether it has sufficient permission to fetch data and communicate its identity to the API. The authentication feature provides a secure way to configure authentication using a variety of methods.

The credentials itself (e.g. username and password) are _not_ specified as part of the connector, instead they are part of the configuration that is specified by the end user when setting up a source based on the connector. During development, it's possible to provide testing credentials in the "Testing values" menu, but those are not saved along with the connector. Credentials that are part of the source configuration are stored in a secure way in your Airbyte instance while the connector configuration is saved in the regular database.

In the "Authentication" section on the "Global Configuration" page in the connector builder, the authentication method can be specified. This configuration is shared for all streams - it's not possible to use different authentication methods for different streams in the same connector. In case your API uses multiple or custom authentication methods, you can use the [low-code CDK](/platform/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/platform/connector-development/cdk-python/).

If your API doesn't need authentication, leave it set at "No auth". This means the connector will be able to make requests to the API without providing any credentials which might be the case for some public open APIs or private APIs only available in local networks.

<iframe width="640" height="430" src="https://www.loom.com/embed/4e65a2090134478d920764b43d1eaef4" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

## Authentication methods

Check the documentation of the API you want to integrate for the used authentication method. The following ones are supported in the connector builder:

- [Basic HTTP](#basic-http)
- [Bearer Token](#bearer-token)
- [API Key](#api-key)
- [JWT Authenticator](#jwt)
- [OAuth2](#oauth-2)
- [Session Token](#session-token)
- [Selective Authenticator](#selective-authenticator)
- [Shared Authenticator](#shared-authenticator)

Select the matching authentication method for your API and check the sections below for more information about individual methods.

### Basic HTTP

If requests are authenticated using the Basic HTTP authentication method, the documentation page will likely contain one of the following keywords:

- "Basic Auth"
- "Basic HTTP"
- "Authorization: Basic"

The Basic HTTP authentication method is a standard and doesn't require any further configuration. Username and password are set via "Testing values" in the connector builder and by the end user when configuring this connector as a Source.

#### Example

The [Greenhouse API](https://developers.greenhouse.io/harvest.html#authentication) is an API using basic authentication.

Sometimes, only a username and no password is required, like for the [Chargebee API](https://apidocs.chargebee.com/docs/api/auth?prod_cat_ver=2) - in these cases simply leave the password input empty.

In the basic authentication scheme, the supplied username and password are concatenated with a colon `:` and encoded using the base64 algorithm. For username `user` and password `passwd`, the base64-encoding of `user:passwd` is `dXNlcjpwYXNzd2Q=`.

When fetching records, this string is sent as part of the `Authorization` header:

```
curl -X GET \
  -H "Authorization: Basic dXNlcjpwYXNzd2Q=" \
  https://harvest.greenhouse.io/v1/<stream path>
```

### Bearer Token

If requests are authenticated using Bearer authentication, the documentation will probably mention "bearer token" or "token authentication". In this scheme, the `Authorization` header of the HTTP request is set to `Bearer <token>`.

Like the Basic HTTP authentication it does not require further configuration. The bearer token can be set via "Testing values" in the connector builder and by the end user when configuring this connector as a Source.

#### Example

The [Sendgrid API](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/authentication) and the [Square API](https://developer.squareup.com/docs/build-basics/access-tokens) are supporting Bearer authentication.

When fetching records, the token is sent along as the `Authorization` header:

```
curl -X GET \
  -H "Authorization: Bearer <bearer token>" \
  https://api.sendgrid.com/<stream path>
```

### API Key

The API key authentication method is similar to the Bearer authentication but allows to configure where to inject the API key (header, request param or request body), as well as under which field name. The used injection mechanism and the field name is part of the connector definition while the API key itself can be set via "Testing values" in the connector builder as well as when configuring this connector as a Source.

The following table helps with which mechanism to use for which API:

| Description                                                        | Injection mechanism |
| ------------------------------------------------------------------ | ------------------- |
| (HTTP) header                                                      | `header`            |
| Query parameter / query string / request parameter / URL parameter | `request_parameter` |
| Form encoded request body / form data                              | `body_data`         |
| JSON encoded request body                                          | `body_json`         |

#### Example

The [CoinAPI.io API](https://docs.coinapi.io/market-data/rest-api#authorization) is using API key authentication via the `X-CoinAPI-Key` header.

When fetching records, the api token is included in the request using the configured header:

```
curl -X GET \
  -H "X-CoinAPI-Key: <api-key>" \
  https://rest.coinapi.io/v1/<stream path>
```

In this case the injection mechanism is `header` and the field name is `X-CoinAPI-Key`.

### JWT

If requests are authenticated using JWT (JSON Web Token) authentication, the API documentation will likely mention one of the following:

- "JWT authentication"
- "JSON Web Token"
- "Bearer JWT"
- "Signed tokens"

JWT authentication generates a signed token using a secret key and algorithm, which is then sent with each request. The connector builder supports various JWT algorithms and configuration options.

#### Configuration

The JWT authentication method requires the following configuration:

- **Secret Key** - The secret key used to sign the JWT token. This can be set via "Testing values" in the connector builder and by the end user when configuring this connector as a Source.
- **Algorithm** - The algorithm used to sign the token. Supported algorithms include:
  - HS256 (HMAC with SHA-256)
  - HS384 (HMAC with SHA-384) 
  - HS512 (HMAC with SHA-512)
  - RS256 (RSA with SHA-256)
  - RS384 (RSA with SHA-384)
  - RS512 (RSA with SHA-512)
  - ES256 (ECDSA with SHA-256)
  - ES384 (ECDSA with SHA-384)
  - ES512 (ECDSA with SHA-512)
- **Base64 Encode Secret Key** - When enabled, the secret key will be base64 encoded before being used to sign the JWT. Only enable this if required by the API.
- **Header Prefix** - The prefix to use in the Authorization header (defaults to "Bearer")
- **JWT Headers** - Additional headers to include in the JWT header object
- **JWT Payload** - Additional properties to include in the JWT payload
- **Additional JWT Headers** - Extra headers to include with the JWT headers object
- **Additional JWT Payload** - Extra properties to add to the JWT payload

#### Example

When fetching records, the JWT token is generated and sent as part of the `Authorization` header:

```
curl -X GET \
  -H "Authorization: Bearer <jwt-token>" \
  https://api.example.com/<stream path>
```

The JWT token is automatically generated by the connector using the configured secret key and algorithm, and includes any additional headers or payload properties you've specified.

### OAuth 2.0 (Declarative)

Declarative OAuth 2.0 provides a comprehensive way to configure any OAuth 2.0 flow by describing the exact structure and behavior of the authentication endpoints. This is the recommended approach for implementing OAuth 2.0 authentication in the Connector Builder, as it supports the complete OAuth flow including user consent and automatic token management.

#### Key Features

- **Complete OAuth 2.0 Flow** - Supports the full authorization code flow with user consent
- **Flexible Configuration** - Accommodates OAuth 2.0 implementations that deviate from standard specifications
- **Automatic Token Management** - Handles access token refresh automatically
- **Custom Parameter Support** - Allows injection of custom parameters and headers at each step

#### Configuration Components

The Declarative OAuth 2.0 configuration consists of three main components:

1. **Consent URL Configuration** - Defines how to construct the URL where users grant consent:
   - URL template with placeholders for client ID, redirect URI, state, and other parameters
   - Support for custom scopes and additional query parameters
   - Configurable parameter names (e.g., custom client_id field names)

2. **Access Token URL Configuration** - Specifies how to exchange the authorization code for an access token:
   - Token endpoint URL with parameter placeholders
   - Configurable placement of client credentials and authorization code
   - Custom headers and query parameters for the token request
   - Response parsing configuration for access token and expiration

3. **Optional Refresh Token Configuration** - Defines how to refresh expired access tokens:
   - Refresh token endpoint URL (if different from access token URL)
   - Custom parameter placement for client credentials and refresh token
   - Configurable header and body parameters

#### Configuration Options

- **Client ID Key** - Custom field name for client_id parameter (defaults to "client_id")
- **Client Secret Key** - Custom field name for client_secret parameter (defaults to "client_secret")
- **Authorization Code Key** - Custom field name for authorization code parameter (defaults to "code")
- **Redirect URI Key** - Custom field name for redirect_uri parameter (defaults to "redirect_uri")
- **Scopes** - Space-separated list of OAuth scopes to request
- **Access Token Key** - Field name in response containing the access token (defaults to "access_token")
- **Access Token Headers** - Custom headers to include in access token requests
- **Access Token Parameters** - Custom query parameters for access token requests

#### Example Configuration

For an API that uses standard OAuth 2.0 with custom parameter names:

- **Consent URL**: `https://api.example.com/oauth/authorize?client_id={{client_id_value}}&redirect_uri={{redirect_uri_value}}&scope={{scope_value}}&state={{state_value}}`
- **Access Token URL**: `https://api.example.com/oauth/token`
- **Scopes**: `read write`

When a user authenticates, they'll be redirected to the consent URL to grant permissions, then the connector will automatically exchange the authorization code for an access token.

To learn more about Declarative OAuth 2.0 and see additional example implementations, please refer to the [Declarative OAuth 2.0](/platform/connector-development/config-based/advanced-topics/oauth) documentation.

### OAuth (Legacy)

The legacy OAuth flow is a simpler approach that allows you to use an existing access token or refresh token to authenticate with the API. This method is useful when you already have OAuth credentials or when the API doesn't support the full OAuth 2.0 authorization code flow.

**Important**: This method requires you to manually obtain the initial OAuth tokens outside of Airbyte. You'll need to implement the initial OAuth flow yourself to get the `access_token` and `refresh_token`, then provide them to the connector as part of the configuration.

The legacy OAuth authentication method implements authentication using OAuth 2.0 with [refresh token grant type](https://oauth.net/2/grant-types/refresh-token/) and [client credentials grant type](https://oauth.net/2/grant-types/client-credentials/).

In this approach, the OAuth endpoint of an API is called with client ID and client secret and/or a long-lived refresh token that you provide when configuring the connector as a Source. These credentials are used to obtain a short-lived access token that's used for making requests to extract records. If the access token expires, the connector will automatically request a new one.

The connector needs to be configured with the endpoint to call to obtain access tokens using the client ID/secret and/or the refresh token. OAuth client ID/secret and the refresh token are provided via "Testing values" in the connector builder as well as when configuring this connector as a Source.

Depending on how the refresh endpoint is implemented, additional configuration might be necessary to specify how to request an access token with the right permissions and how to extract the access token and expiry date from the response:

- **Scopes** - The [OAuth scopes](https://oauth.net/2/scope/) the access token will have access to. If not specified, no scopes are sent with the refresh token request
- **Grant type** - The OAuth grant type to use (either "refresh_token" or "client_credentials"). When using "refresh_token", a refresh token must be provided by the end user when configuring the connector as a Source
- **Token expiry property name** - The name of the property in the response that contains token expiry information. If not specified, defaults to `expires_in`
- **Token expiry property date format** - If not specified, the expiry property is interpreted as the number of seconds the access token will be valid
- **Access token property name** - The name of the property in the response that contains the access token for making requests. If not specified, defaults to `access_token`

If the API uses other grant types (like PKCE), you may need to use the [low-code CDK](/platform/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/platform/connector-development/cdk-python/) instead.

**Note**: The legacy OAuth authentication method does not provide a single-click authentication experience for end users. Users will still need to manually obtain the client ID, client secret, and refresh token from the API and enter them into the configuration form. For a complete OAuth flow with user consent, use [OAuth 2.0 (Declarative)](#oauth-20-declarative) instead.

#### Example

The [Square API](https://developer.squareup.com/docs/build-basics/access-tokens#get-an-oauth-access-token) supports OAuth.

In this case, the authentication method has to be configured like this:

- "Token refresh endpoint" is `https://connect.squareup.com/oauth2/token`
- "Token expiry property name" is `expires_at`

When running a sync, the connector is first sending client id, client secret and refresh token to the token refresh endpoint:

```

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"client_id": "<client id>", "client_secret": "<client secret>", "refresh_token": "<refresh token>", "grant_type": "refresh_token" }' \
  <token refresh endpoint>
```

The response is a JSON object containing an `access_token` property and an `expires_at` property:

```
 {"access_token":"<access-token>", "expires_at": "2023-12-12T00:00:00"}
```

The `expires_at` date tells the connector how long the access token can be used - if this point in time is passed, a new access token is requested automatically.

When fetching records, the access token is sent along as part of the `Authorization` header:

```
curl -X GET \
  -H "Authorization: Bearer <access-token>" \
  https://connect.squareup.com/v2/<stream path>
```

#### Single-Use Refresh Tokens

In most cases, OAuth refresh tokens are long-lived and can be reused to create access tokens for every sync. However, some APIs invalidate the refresh token after each use and return a new refresh token along with the access token. One example of this behavior is the [Smartsheets API](https://smartsheet.redoc.ly/#section/OAuth-Walkthrough/Get-or-Refresh-an-Access-Token).

For APIs that use single-use refresh tokens, you can enable the "Overwrite config with refresh token response" setting. When enabled:

- The authenticator expects a new refresh token to be returned from the token refresh endpoint
- By default, the property `refresh_token` is used to extract the new refresh token, but this can be configured using the "Refresh token property name" setting
- The connector automatically updates its configuration with the new refresh token for the next sync
- You must specify an initial access token along with its expiry date in the "Testing values" menu when using this option

This ensures that the connector can continue to authenticate successfully even when refresh tokens are single-use.

### Session Token

Some APIs require callers to first fetch a unique token from one endpoint, then make the rest of their calls to all other endpoints using that token to authenticate themselves. These tokens usually have an expiration time, after which a new token needs to be re-fetched to continue making requests. This flow can be achieved through using the Session Token Authenticator.

If requests are authenticated using the Session Token authentication method, the API documentation page will likely contain one of the following keywords:

- "Session Token"
- "Session ID"
- "Auth Token"
- "Access Token"
- "Temporary Token"

#### Configuration

The configuration of a Session Token authenticator is a bit more involved than other authenticators, as you need to configure both how to make requests to the session token retrieval endpoint (which requires its own authentication method), as well as how the token is extracted from that response and used for the data requests.

We will walk through each part of the configuration below. Throughout this, we will refer to the [Metabase API](https://www.metabase.com/learn/administration/metabase-api#authenticate-your-requests-with-a-session-token) as an example of an API that uses session token authentication.

- `Session Token Retrieval` - This is a group of fields which configures how the session token is fetched from the session token endpoint in your API. Once the session token is retrieved, your connector will reuse that token until it expires, at which point it will retrieve a new session token using this configuration.
  - `URL` - the full URL of the session token endpoint
    - For Metabase, this would be `https://<app_name>.metabaseapp.com/api/session`.
  - `HTTP Method` - the HTTP method that should be used when retrieving the session token endpoint, either `GET` or `POST`
    - Metabase requires `POST` for its `/api/session` requests.
  - `Authentication Method` - configures the method of authentication to use **for the session token retrieval request only**
    - Note that this is separate from the parent Session Token Authenticator. It contains the same options as the parent Authenticator Method dropdown, except for OAuth (which is unlikely to be used for obtaining session tokens) and Session Token (as it does not make sense to nest).
    - For Metabase, the `/api/session` endpoint takes in a `username` and `password` in the request body. Since this is a non-standard authentication method, we must set this inner `Authentication Method` to `No Auth`, and instead configure the `Request Body` to pass these credentials (discussed below).
  - `Query Parameters` - used to attach query parameters to the session token retrieval request
    - Metabase does not require any query parameters in the `/api/session` request, so this is left unset.
  - `Request Headers` - used to attach headers to the session token retrieval request
    - Metabase does not require any headers in the `/api/session` request, so this is left unset.
  - `Request Body` - used to attach a request body to the session token retrieval request
    - As mentioned above, Metabase requires the username and password to be sent in the request body, so we can select `JSON (key-value pairs)` here and set the username and password fields (using User Inputs for the values to make the connector reusable), so this would end up looking like:
      - Key: `username`, Value: `{{ config['username'] }}`
      - Key: `password`, Value: `{{ config['password'] }}`
  - `Error Handler` - used to handle errors encountered when retrieving the session token
    - See the [Error Handling](/platform/connector-development/connector-builder-ui/error-handling) page for more info about configuring this component.
- `Session Token Path` - An array of values to form a path into the session token retrieval response which points to the session token value
  - For Metabase, the `/api/session` response looks like `{"id":"<session-token-value>"}`, so the value here would simply be `id`.
- `Expiration Duration` - An [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations) indicating how long the session token has until it expires
  - Once this duration is reached, your connector will automatically fetch a new session token, and continue making data requests with that new one.
  - If this is left unset, the session token will be refreshed before every single data request. This is **not recommended** if it can be avoided, as this will cause the connector to run much slower, as it will need to make an extra token request for every data request.
  - **Note**: This **does not support dynamic expiration durations of session tokens**. If your token expiration duration is dynamic, you should set the `Expiration Duration` field to the expected minimum duration to avoid problems during syncing.
  - For Metabase, the token retrieved from the `/api/session` endpoint expires after 14 days by default, so this value can be set to `P2W` or `P14D`.
- `Data Request Authentication` - Configures how the session token is used to authenticate the data requests made to the API
  - Choose `API Key` if your session token needs to be injected into a query parameter or header of the data requests.
    - Metabase takes in the session token through a specific header, so this would be set to `API Key`, Inject Session Token into outgoing HTTP Request would be set to `Header`, and Header Name would be set to `X-Metabase-Session`.
  - Choose `Bearer` if your session token needs to be sent as a standard Bearer token.

## Selective Authenticator

Selective Authenticator allows you to dynamically choose between different authentication methods based on a configuration property value. This is useful when your connector needs to support multiple authentication options and let users select which one to use.

### Configuration

- **Authenticator Selection Path**: An array of strings defining the path in the configuration to the property that determines which authenticator to use
- **Authenticators**: A mapping of authenticator names to their respective configurations

### How it works

The Selective Authenticator evaluates the value at the specified configuration path and uses it to select the appropriate authenticator from the available options. For example, if the selection path points to a config property with value "api_key", it will use the authenticator mapped to "api_key".

### Example

If you want to support both API Key and OAuth authentication:

1. **Authenticator Selection Path**: `["auth", "type"]`
2. **Authenticators**: 
   - `api_key`: Configure an API Key authenticator
   - `oauth`: Configure an OAuth authenticator

When users configure their connector, they would set `auth.type` to either "api_key" or "oauth", and the Selective Authenticator will automatically use the corresponding authentication method.

### Use Cases

- APIs that support multiple authentication methods
- Connectors that need to work with different API versions requiring different auth
- Providing flexibility for users to choose their preferred authentication method

## Shared Authenticator

Shared Authenticator is a UI feature that allows you to share authenticator configurations across different parts of your connector. This helps reduce duplication and ensures consistency when the same authentication method is used in multiple places.

### How it works

In the Connector Builder UI, you'll see a link icon with a toggle switch next to authenticator fields that can be shared. This feature allows you to:

- **Link configurations**: Share the same authenticator configuration across multiple components
- **Unlink configurations**: Use different authenticator settings for specific components
- **Resolve conflicts**: When there are different values, a dialog helps you choose which one to use

### Using Shared Authenticators

1. **Enable sharing**: Click the link toggle to share an authenticator configuration
2. **Manage conflicts**: If there are different values between shared and local configurations, you'll see a dialog asking which value to use
3. **Disable sharing**: Toggle off to use a local configuration instead of the shared one

### Benefits

- **Consistency**: Ensures the same authentication method is used across your connector
- **Efficiency**: Reduces the need to configure the same authenticator multiple times
- **Maintenance**: Changes to shared authenticators automatically apply everywhere they're used

### Example

If your connector uses the same API key authentication for both data retrieval and metadata requests, you can configure the API key once and share it across both components using the Shared Authenticator feature.

### Custom authentication methods

Some APIs require complex custom authentication schemes involving signing requests or doing multiple requests to authenticate. In these cases, it's required to use the [low-code CDK](/platform/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/platform/connector-development/cdk-python/).
