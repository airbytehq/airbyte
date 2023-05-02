# Authentication

Authentication allows the connector to check whether it has sufficient permission to fetch data and communicate its identity to the API. The authentication feature provides a secure way to configure authentication using a variety of methods.

The credentials itself (e.g. username and password) are _not_ specified as part of the connector, instead they are part of the configuration that is specified by the end user when setting up a source based on the connector. During development, it's possible to provide testing credentials in the "Testing values" menu, but those are not saved along with the connector. Credentials that are part of the source configuration are stored in a secure way in your Airbyte instance while the connector configuration is saved in the regular database.

In the "Authentication" section on the "Global Configuration" page in the connector builder, the authentication method can be specified. This configuration is shared for all streams - it's not possible to use different authentication methods for different streams in the same connector. In case your API uses multiple or custom authentication methods, you can use the [low-code CDK](/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/connector-development/cdk-python/).

If your API doesn't need authentication, leave it set at "No auth". This means the connector will be able to make requests to the API without providing any credentials which might be the case for some public open APIs or private APIs only available in local networks.

<iframe width="640" height="430" src="https://www.loom.com/embed/4e65a2090134478d920764b43d1eaef4" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

## Authentication methods

Check the documentation of the API you want to integrate for the used authentication method. The following ones are supported in the connector builder:
* [Basic HTTP](#basic-http)
* [Bearer Token](#bearer-token)
* [API Key](#api-key)
* [OAuth](#oauth)

Select the matching authentication method for your API and check the sections below for more information about individual methods.

### Basic HTTP

If requests are authenticated using the Basic HTTP authentication method, the documentation page will likely contain one of the following keywords:
- "Basic Auth"
- "Basic HTTP"
- "Authorization: Basic"
- "Base64"

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

The API key authentication method is similar to the Bearer authentication but allows to configure as which HTTP header the API key is sent as part of the request. The http header name is part of the connector definition while the API key itself can be set via "Testing values" in the connector builder as well as when configuring this connector as a Source.

This form of authentication is often called "(custom) header authentication". It only supports setting the token to an HTTP header, for other cases, see the ["Other authentication methods" section](#access-token-as-query-or-body-parameter)

#### Example

The [CoinAPI.io API](https://docs.coinapi.io/market-data/rest-api#authorization) is using API key authentication via the `X-CoinAPI-Key` header.

When fetching records, the api token is included in the request using the configured header:
```
curl -X GET \
  -H "X-CoinAPI-Key: <api-key>" \
  https://rest.coinapi.io/v1/<stream path>
```

### OAuth

The OAuth authentication method implements authentication using an [OAuth2.0 flow with a refresh token grant type](https://oauth.net/2/grant-types/refresh-token/).

In this scheme, the OAuth endpoint of an API is called with a long-lived refresh token that's provided by the end user when configuring this connector as a Source. The refresh token is used to obtain a short-lived access token that's used to make requests actually extracting records. If the access token expires, the connection will automatically request a new one.

The connector needs to be configured with the endpoint to call to obtain access tokens with the refresh token. OAuth client id/secret and the refresh token are provided via "Testing values" in the connector builder as well as when configuring this connector as a Source.

Depending on how the refresh endpoint is implemented exactly, additional configuration might be necessary to specify how to request an access token with the right permissions (configuring OAuth scopes and grant type) and how to extract the access token and the expiry date out of the response (configuring expiry date format and property name as well as the access key property name):
* **Scopes** - the [OAuth scopes](https://oauth.net/2/scope/) the access token will have access to. if not specified, no scopes are sent along with the refresh token request
* **Token expiry property name** - the name of the property in the response that contains token expiry information. If not specified, it's set to `expires_in`
* **Token expire property date format** - if not specified, the expiry property is interpreted as the number of seconds the access token will be valid
* **Access token property name** - the name of the property in the response that contains the access token to do requests. If not specified, it's set to `access_token`

If the API uses a short-lived refresh token that expires after a short amount of time and needs to be refreshed as well or if other grant types like PKCE are required, it's not possible to use the connector builder with OAuth authentication - check out the [compatibility guide](/connector-development/connector-builder-ui/connector-builder-compatibility#oauth) for more information.

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

### Other authentication methods

If your API is not using one of the natively supported authentication methods, it's still possible to build an Airbyte connector as described below.

#### Access token as query or body parameter

Some APIs require to include the access token in different parts of the request (for example as a request parameter). For example, the [Breezometer API](https://docs.breezometer.com/api-documentation/introduction/#authentication) is using this kind of authentication. In these cases it's also possible to configure authentication manually:
* Add a user input as secret field on the "User inputs" page (e.g. named `api_key`)
* On the stream page, add a new "Request parameter"
* As key, configure the name of the query parameter the API requires (e.g. named `key`)
* As value, configure a [placeholder](/connector-development/config-based/understanding-the-yaml-file/reference#variables) for the created user input (e.g. `{{ config['api_key'] }}`)

<iframe width="640" height="396" src="https://www.loom.com/embed/1d62a8cce4304ee7ac45e748bd9c29be" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

The same approach can be used to add the token to the request body.

#### Custom authentication methods

Some APIs require complex custom authentication schemes involving signing requests or doing multiple requests to authenticate. In these cases, it's required to use the [low-code CDK](/connector-development/config-based/low-code-cdk-overview) or [Python CDK](/connector-development/cdk-python/).
