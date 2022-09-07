# Authentication

The `Authenticator` defines how to configure outgoing HTTP requests to authenticate on the API source.

## Authenticators

### ApiKeyAuthenticator

The `ApiKeyAuthenticator` sets an HTTP header on outgoing requests.
The following definition will set the header "Authorization" with a value "Bearer hello":

```yaml
authenticator:
  type: "ApiKeyAuthenticator"
  header: "Authorization"
  token: "Bearer hello"
```

### BearerAuthenticator

The `BearerAuthenticator` is a specialized `ApiKeyAuthenticator` that always sets the header "Authorization" with the value "Bearer {token}".
The following definition will set the header "Authorization" with a value "Bearer hello"

```yaml
authenticator:
  type: "BearerAuthenticator"
  token: "hello"
```

More information on bearer authentication can be found [here](https://swagger.io/docs/specification/authentication/bearer-authentication/).

### BasicHttpAuthenticator

The `BasicHttpAuthenticator` set the "Authorization" header with a (USER ID/password) pair, encoded using base64 as per [RFC 7617](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
The following definition will set the header "Authorization" with a value "Basic {encoded credentials}"

```yaml
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
  password: "world"
```

The password is optional. Authenticating with APIs using Basic HTTP and a single API key can be done as:

```yaml
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
```

### OAuth

OAuth authentication is supported through the `OAuthAuthenticator`, which requires the following parameters:

- token_refresh_endpoint: The endpoint to refresh the access token
- client_id: The client id
- client_secret: The client secret
- refresh_token: The token used to refresh the access token
- scopes (Optional): The scopes to request. Default: Empty list
- token_expiry_date (Optional): The access token expiration date formatted as RFC-3339 ("%Y-%m-%dT%H:%M:%S.%f%z")
- access_token_name (Optional): The field to extract access token from in the response. Default: "access_token".
- expires_in_name (Optional): The field to extract expires_in from in the response. Default: "expires_in"
- refresh_request_body (Optional): The request body to send in the refresh request. Default: None

```yaml
authenticator:
  type: "OAuthAuthenticator"
  token_refresh_endpoint: "https://api.searchmetrics.com/v4/token"
  client_id: "{{ config['api_key'] }}"
  client_secret: "{{ config['client_secret'] }}"
  refresh_token: ""
```