# Authentication

Authentication is about providing some form of confidental secret (credentials, password, token, key) to the API provider that identifies the caller (in this case the connector). It allows the provider to check whether the caller is known and has sufficient permission to fetch data. The authentication feature provides a secure way to configure authentication using a variety of methods.

The credentials itself (e.g. username and password) are _not_ specified as part of the connector, instead they are part of the source configration that is specified by the end user when setting up a source based on the connector. During development, it's possible to provide testing credentials in the "Testing values" menu, but those are not saved along with the connector. Credentials that are part of the source configuration are stored in a secure way in your Airbyte instance while the connector configuration is saved in the regular database.

In the "Authentication" section on the "Global Configuration" page in the connector builder, the authentication method can be specified. This configuration is shared for all streams - it's not possible to use different authentication methods for different streams in the same connector.

If your API doesn't need authentication, leave it set at "No auth". This means the connector will be able to make requests to the API without providing any credentials which might be the case for some public open APIs or private APIs only available in local networks.

## Authentication methods

Check the documentation of the API you want to integrate for the used authentication method. The following ones are supported in the connector builder:
* [Basic HTTP](#basic-http)
* [Bearer](#bearer)
* [API Key](#api-key)
* [OAuth](#oauth)
* [Session token](#session-token)

Select the matching authentication method for your API and check the sections below for more information about individual methods.

### Basic HTTP

If requests are authenticated using the Basic HTTP authentication method, the documentation page will likely contain one of the following keywords:
- "Basic Auth"
- "Basic HTTP"
- "Authorization: Basic"
- "Base64"

The Basic HTTP authentication method is a standard and doesn't require any further configuration. Username and password are set via "Testing values" in the connector builder and as part of the source configuration when configuring connections.

#### Example

The [Greenhouse API](https://developers.greenhouse.io/harvest.html#introduction) is an API using basic auth.

Sometimes, only a username and no password is required, like for the [Chargebee API](https://apidocs.chargebee.com/docs/api/auth?prod_cat_ver=2) - in these cases simply leave the password input empty.

In the basic auth scheme, the supplied username and password are concatenated with a colon `:` and encoded using the base64 algorithm. For username `user` and password `passwd`, the base64-encoding of `user:passwd` is `dXNlcjpwYXNzd2Q=`.

When fetching records, this string is sent as part of the `Authorization` header:
```
curl -X GET \
  -H "Authorization: Basic dXNlcjpwYXNzd2Q=" \
  https://harvest.greenhouse.io/v1/<stream path>
```

### Bearer

If requests are authenticated using Bearer authentication, the documentation will probably mention "bearer token" or "token authentication". In this scheme, the `Authorization` header of the HTTP request is set to `Bearer <token>`.

Like the Basic HTTP authentication it does not require further configuration. The bearer token can be set via "Testing values" in the connector builder as well as paert of the source configuration when configuring connections.

#### Example

The [Sendgrid API](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/authentication) and the [Square API](https://developer.squareup.com/docs/build-basics/access-tokens) are supporting Bearer authentication.

When fetching records, the token is sent along as the `Authorization` header:
```
curl -X GET \
  -H "Authorization: Bearer <bearer token>" \
  https://api.sendgrid.com/<stream path>
```

### API Key

The API key authentication method is similar to the Bearer authentication but allows to configure as which HTTP header the API key is sent as part of the request. The http header name is part of the connector definition while the API key itself can be set via "Testing values" in the connector builder as well as part of the source configuration when configuring connections.

This form of authentication is often called "(custom) header authentication".

#### Example

The [CoinAPI.io API](https://docs.coinapi.io/market-data/rest-api#authorization) is using API key authentication via the `X-CoinAPI-Key` header.

When fetching records, the api token is sent along as the configured header:
```
curl -X GET \
  -H "X-CoinAPI-Key: <api-key>" \
  https://rest.coinapi.io/v1/<stream path>
```

### OAuth

The OAuth authentication method implements authentication using an OAuth2.0 flow with a refresh token grant type.

In this scheme the OAuth endpoint of an API is called with a long-lived refresh token provided as part of the source configuration to obtain a short-lived access token that's used to make requests actually extracting records. If the access token expires, a new one is requested automatically.

It needs to be configured with the endpoint to call to obtain access tokens with the refresh token. OAuth client id/secret and the refresh token are provided via "Testing values" in the connector builder as well as part of the source configuration when configuring connections.


Depending on how the refresh endpoint is implemented exactly, additional configuration might be necessary to specify how to request an access token with the right permissions (configuring OAuth scopes and grant type) and how to extract the access token and the expiry date out of the response (configuring expiry date format and property name as well as the access key property name):
* Scopes - if not specified, no scopes are sent along with the refresh token request
* Grant type - if not specified, it's set to `refresh_token`
* Token expiry property name - if not specified, it's set to `expires_in`
* Token expire property date format - if not specified, the expiry property is interpreted as the number of seconds the access token will be valid
* Access token property name - the name of the property in the response that contains the access token to do requests. If not specified, it's set to `access_token`

If the refresh token itself isn't long lived but expires after a short amount of time and needs to be refresh as well or if other grant types like PKCE are required, it's not possible to use the connector builder with OAuth authentication - check out the [compatibility guide](http://localhost:3000/connector-development/config-based/connector-builder-compatibility#oauth) for more information.

Keep in mind that the OAuth authentication method does not implement a single-click authentication experience for the end user configuring the connector - it will still be necessary to obtain client id, client secret and refresh token from the API and manually enter them into the configuration form.

#### Example

The [Square API](https://developer.squareup.com/docs/build-basics/access-tokens#get-an-oauth-access-token) supports OAuth.

In this case, the authentication method has to be configured like this:
* "Token refresh endpoint" is `https://connect.squareup.com/oauth2/token`
* "Token expiry property name" is `expires_at`

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


### Session token

The session token authentication method is the right choice if the API requires a consumer to send a request to "log in", returning a session token which can be used to send request actually extracting records.

Username and password are supplied as "Testing values" / as part of the source configuration and are sent to the configured "Login url" as a JSON body with a `username` and a `password` property. The "Session token response key" specifies where to find the session token in the log-in response. The "Header" specifies in which HTTP header field the session token has to be injected.

Besides specifying username and password, the session token authentication method also allows 

to directly specify the session token via the source configuration. In this case, the "Validate session url" is used to check whether the provided session token is still valid.

#### Example

The [Metabase API](https://www.metabase.com/learn/administration/metabase-api#authenticate-your-requests-with-a-session-token) is providing a session authentication scheme.

In this case, the authentication method has to be configured like this:
* "Login url" is `session`
* "Session token response key" is `id`
* "Header" is `X-Metabase-Session`
* "Validate session url" is `user/current`

When running a sync, the connector is first sending username and password to the `session` 
endpoint:
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "<username>", "password": "<password>"}' \
  http://<base url>/session
```

The response is a JSON object containing an `id` property:
```
 {"id":"<session-token>"}
```

When fetching records, the session token is sent along as the `X-Metabase-Session` header:
```
curl -X GET \
  -H "X-Metabase-Session: <session-token>" \
  http://<base url>/<stream path>
```

If the session token is specified as part of the source configuration, the "Validate session url" is requested with the existing token to check for validity:
```
curl -X GET \
  -H "X-Metabase-Session: <session-token>" \
  http://<base url>/user/current
```

If this request returns an HTTP status code that's not in the range of 400 to 600, the token is considered valid and records are fetched.

## Reference

For detailed documentation of the underlying low code components, see here TODO