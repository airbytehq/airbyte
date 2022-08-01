# Authentication

The `Authenticator` defines how to configure outgoing HTTP requests to authenticate on the API source.

## Authenticators

### ApiKeyAuthenticator

The `ApiKeyAuthenticator` sets an HTTP header on outgoing requests.
The following definition will set the header "Authorization" with a value "Bearer hello":

```
authenticator:
  type: "ApiKeyAuthenticator"
  header: "Authorization"
  token: "Bearer hello"
```

### BearerAuthenticator

The `BearerAuthenticator` is a specialized `ApiKeyAuthenticator` that always sets the header "Authorization" with the value "Bearer {token}".
The following definition will set the header "Authorization" with a value "Bearer hello"

```
authenticator:
  type: "BearerAuthenticator"
  token: "hello"
```

More information on bearer authentication can be found [here](https://swagger.io/docs/specification/authentication/bearer-authentication/)

### BasicHttpAuthenticator

The `BasicHttpAuthenticator` set the "Authorization" header with a (USER ID/password) pair, encoded using base64 as per [RFC 7617](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
The following definition will set the header "Authorization" with a value "Basic <encoded credentials>"

The encoding scheme is:

1. concatenate the username and the password with `":"` in between
2. Encode the resulting string in base 64
3. Decode the result in utf8

```
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
  password: "world"
```

The password is optional. Authenticating with APIs using Basic HTTP and a single API key can be done as:

```
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
```

### OAuth

OAuth authentication is supported through the `OAuthAuthenticator`, which requires the following parameters:

- token_refresh_endpoint: The endpoint to refresh the access token
- client_id: The client id
- client_secret: Client secret
- refresh_token: The token used to refresh the access token
- scopes: The scopes to request
- token_expiry_date: The access token expiration date
- access_token_name: THe field to extract access token from in the response
- expires_in_name:The field to extract expires_in from in the response
- refresh_request_body: The request body to send in the refresh request