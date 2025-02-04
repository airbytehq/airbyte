# Authentication

Authentication allows the connector to check whether it has sufficient permission to fetch data and communicate its identity to the API. The authentication feature provides a secure way to configure authentication using a variety of methods.

The credentials itself (e.g. username and password) are _not_ specified as part of the connector, instead they are part of the configuration that is specified by the end user when setting up a source based on the connector. During development, it's possible to provide testing credentials in the "Testing values" menu, but those are not saved along with the connector. Credentials that are part of the source configuration are stored in a secure way in your Airbyte instance while the connector configuration is saved in the regular database.

In the "Authentication" section on the "Global Configuration" page in the connector builder, the authentication method can be specified. This configuration is shared for all streams - it's not possible to use different authentication methods for different streams in the same connector. In case your API uses multiple or custom authentication methods, you can use the [low-code CDK](/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/connector-development/cdk-python/).

If your API doesn't need authentication, leave it set at "No auth". This means the connector will be able to make requests to the API without providing any credentials which might be the case for some public open APIs or private APIs only available in local networks.

<iframe width="640" height="430" src="https://www.loom.com/embed/4e65a2090134478d920764b43d1eaef4" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

## Authentication methods

Check the documentation of the API you want to integrate for the used authentication method. The following ones are supported in the connector builder:

- [Basic HTTP](#basic-http)
- [Bearer Token](#bearer-token)
- [API Key](#api-key)
- [OAuth](#oauth)
- [Session Token](#session-token)

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

### OAuth

#### Declarative OAuth 2.0
Declarative OAuth 2.0 provides a flexible way to configure any OAuth 2.0 flow by describing the exact structure and behavior of the authentication endpoints. This allows integration with OAuth 2.0 implementations that may deviate from the standard specification or have custom requirements.

The configuration consists of three main components:

1. **Consent URL Configuration** - Defines how to construct the URL where users grant consent:
   - URL template with placeholders for client ID, redirect URI, and other parameters
   - Specification of where parameters should be injected (query params, headers, etc.)
   - Support for custom scopes and additional parameters

2. **Access Token URL Configuration** - Specifies how to exchange the authorization code for an access token:
   - Token endpoint URL
   - Where to place client ID, client secret, and authorization code
   - Response parsing configuration for access token and expiration
   - Support for custom parameters and headers

3. **Optional Refresh Token URL Configuration** - Defines how to refresh expired access tokens:
   - Refresh token endpoint URL (if different from access token URL)
   - Parameter placement for client credentials and refresh token
   - Custom header and body configurations

To learn more about the Declarative OAuth 2.0 add see a variety of example implementations please refer to the [Declarative OAuth 2.0](/connector-development/config-based/advanced-topics/oauth) documentation.


#### Partial OAuth (legacy)

The partial OAuth flow is a simpler flow that allows you to use an existing access (or refresh) token to authenticate with the API.


The catch is that the user needs to implement the start of the OAuth flow manually to obtain the `access_token` and the `refresh_token` and pass them to the connector as a part of the `config` object.


The OAuth authentication method implements authentication using an OAuth2.0 flow with a [refresh token grant type](https://oauth.net/2/grant-types/refresh-token/) and [client credentials grant type](https://oauth.net/2/grant-types/client-credentials/).

In this scheme, the OAuth endpoint of an API is called with client id and client secret and/or a long-lived refresh token that's provided by the end user when configuring this connector as a Source. These credentials are used to obtain a short-lived access token that's used to make requests actually extracting records. If the access token expires, the connection will automatically request a new one.

The connector needs to be configured with the endpoint to call to obtain access tokens with the client id/secret and/or the refresh token. OAuth client id/secret and the refresh token are provided via "Testing values" in the connector builder as well as when configuring this connector as a Source.

Depending on how the refresh endpoint is implemented exactly, additional configuration might be necessary to specify how to request an access token with the right permissions (configuring OAuth scopes and grant type) and how to extract the access token and the expiry date out of the response (configuring expiry date format and property name as well as the access key property name):

- **Scopes** - the [OAuth scopes](https://oauth.net/2/scope/) the access token will have access to. if not specified, no scopes are sent along with the refresh token request
- **Grant type** - the used OAuth grant type (either refresh token or client credentials). In case of refresh_token, a refresh token has to be provided by the end user when configuring the connector as a Source.
- **Token expiry property name** - the name of the property in the response that contains token expiry information. If not specified, it's set to `expires_in`
- **Token expire property date format** - if not specified, the expiry property is interpreted as the number of seconds the access token will be valid
- **Access token property name** - the name of the property in the response that contains the access token to do requests. If not specified, it's set to `access_token`

If the API uses other grant types like PKCE are required, it's not possible to use the connector builder with OAuth authentication - check out the [compatibility guide](/connector-development/connector-builder-ui/connector-builder-compatibility#oauth) for more information.

Keep in mind that the OAuth authentication method does not implement a single-click authentication experience for the end user configuring the connector - it will still be necessary to obtain client id, client secret and refresh token from the API and manually enter them into the configuration form.

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

#### Update refresh token from authentication response

In a lot of cases, OAuth refresh tokens are long-lived and can be used to create access tokens for every sync. In some cases however, a refresh token becomes invalid after it has been used to create an access token. In these situations, a new refresh token is returned along with the access token. One example of this behavior is the [Smartsheets API](https://smartsheet.redoc.ly/#section/OAuth-Walkthrough/Get-or-Refresh-an-Access-Token). In these cases, it's necessary to update the refresh token in the configuration every time an access token is generated, so the next sync will still succeed.

This can be done using the "Overwrite config with refresh token response" setting. If enabled, the authenticator expects a new refresh token to be returned from the token refresh endpoint. By default, the property `refresh_token` is used to extract the new refresh token, but this can be configured using the "Refresh token property name" setting. The connector then updates its own configuration with the new refresh token and uses it the next time an access token needs to be generated. If this option is used, it's necessary to specify an initial access token along with its expiry date in the "Testing values" menu.

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

- `Session Token Retrieval` - this is a group of fields which configures how the session token is fetched from the session token endpoint in your API. Once the session token is retrieved, your connector will reuse that token until it expires, at which point it will retrieve a new session token using this configuration.
  - `URL` - the full URL of the session token endpoint
    - For Metabase, this would be `https://<app_name>.metabaseapp.com/api/session`.
  - `HTTP Method` - the HTTP method that should be used when retrieving the session token endpoint, either `GET` or `POST`
    - Metabase requires `POST` for its `/api/session` requests.
  - `Authentication Method` - configures the method of authentication to use **for the session token retrieval request only**
    - Note that this is separate from the parent Session Token Authenticator. It contains the same options as the parent Authenticator Method dropdown, except for OAuth (which is unlikely to be used for obtaining session tokens) and Session Token (as it does not make sense to nest).
    - For Metabase, the `/api/session` endpoint takes in a `username` and `password` in the request body. Since this is a non-standard authentication method, we must set this inner `Authentication Method` to `No Auth`, and instead configure the `Request Body` to pass these credentials (discussed below).
  - `Query Parameters` - used to attach query parameters to the session token retrieval request
    - Metabase does not require any query parameters in the `/api/session` request, so this is left unset.
  - `Request Headers` - used to attach headers to the sesssion token retrieval request
    - Metabase does not require any headers in the `/api/session` request, so this is left unset.
  - `Request Body` - used to attach a request body to the session token retrieval request
    - As mentioned above, Metabase requires the username and password to be sent in the request body, so we can select `JSON (key-value pairs)` here and set the username and password fields (using User Inputs for the values to make the connector reusable), so this would end up looking like:
      - Key: `username`, Value: `{{ config['username'] }}`
      - Key: `password`, Value: `{{ config['password'] }}`
  - `Error Handler` - used to handle errors encountered when retrieving the session token
    - See the [Error Handling](/connector-development/connector-builder-ui/error-handling) page for more info about configuring this component.
- `Session Token Path` - an array of values to form a path into the session token retrieval response which points to the session token value
  - For Metabase, the `/api/session` response looks like `{"id":"<session-token-value>"}`, so the value here would simply be `id`.
- `Expiration Duration` - an [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations) indicating how long the session token has until it expires
  - Once this duration is reached, your connector will automatically fetch a new session token, and continue making data requests with that new one.
  - If this is left unset, the session token will be refreshed before every single data request. This is **not recommended** if it can be avoided, as this will cause the connector to run much slower, as it will need to make an extra token request for every data request.
  - Note: this **does _not_ support dynamic expiration durations of session tokens**. If your token expiration duration is dynamic, you should set the `Expiration Duration` field to the expected minimum duration to avoid problems during syncing.
  - For Metabase, the token retrieved from the `/api/session` endpoint expires after 14 days by default, so this value can be set to `P2W` or `P14D`.
- `Data Request Authentication` - configures how the session token is used to authenticate the data requests made to the API
  - Choose `API Key` if your session token needs to be injected into a query parameter or header of the data requests.
    - Metabase takes in the session token through a specific header, so this would be set to `API Key`, Inject Session Token into outgoing HTTP Request would be set to `Header`, and Header Name would be set to `X-Metabase-Session`.
  - Choose `Bearer` if your session token needs to be sent as a standard Bearer token.

### Custom authentication methods

Some APIs require complex custom authentication schemes involving signing requests or doing multiple requests to authenticate. In these cases, it's required to use the [low-code CDK](/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/connector-development/cdk-python/).
