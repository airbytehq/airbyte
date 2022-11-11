# Authentication

The `Authenticator` defines how to configure outgoing HTTP requests to authenticate on the API source.

Schema:

```yaml
  Authenticator:
    type: object
    description: "Authenticator type"
    anyOf:
      - "$ref": "#/definitions/OAuth"
      - "$ref": "#/definitions/ApiKeyAuthenticator"
      - "$ref": "#/definitions/BearerAuthenticator"
      - "$ref": "#/definitions/BasicHttpAuthenticator"
```

## Authenticators

### ApiKeyAuthenticator

The `ApiKeyAuthenticator` sets an HTTP header on outgoing requests.
The following definition will set the header "Authorization" with a value "Bearer hello":

Schema:

```yaml
  ApiKeyAuthenticator:
    type: object
    additionalProperties: true
    required:
      - header
      - api_token
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      header:
        type: string
      api_token:
        type: string
```

Example:

```yaml
authenticator:
  type: "ApiKeyAuthenticator"
  header: "Authorization"
  api_token: "Bearer hello"
```

### BearerAuthenticator

The `BearerAuthenticator` is a specialized `ApiKeyAuthenticator` that always sets the header "Authorization" with the value "Bearer {token}".
The following definition will set the header "Authorization" with a value "Bearer hello"

Schema:

```yaml
  BearerAuthenticator:
    type: object
    additionalProperties: true
    required:
      - api_token
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      api_token:
        type: string
```

Example:

```yaml
authenticator:
  type: "BearerAuthenticator"
  api_token: "hello"
```

More information on bearer authentication can be found [here](https://swagger.io/docs/specification/authentication/bearer-authentication/).

### BasicHttpAuthenticator

The `BasicHttpAuthenticator` set the "Authorization" header with a (USER ID/password) pair, encoded using base64 as per [RFC 7617](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
The following definition will set the header "Authorization" with a value "Basic {encoded credentials}"

Schema:

```yaml
  BasicHttpAuthenticator:
    type: object
    additionalProperties: true
    required:
      - username
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      username:
        type: string
      password:
        type: string
```

Example:

```yaml
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
  password: "world"
```

The password is optional. Authenticating with APIs using Basic HTTP and a single API key can be done as:

Example:

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
- grant_type (Optional): The parameter specified grant_type to request access_token. Default: "refresh_token"

Schema:

```yaml
  OAuth:
    type: object
    additionalProperties: true
    required:
      - token_refresh_endpoint
      - client_id
      - client_secret
      - refresh_token
      - access_token_name
      - expires_in_name
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      token_refresh_endpoint:
        type: string
      client_id:
        type: string
      client_secret:
        type: string
      refresh_token:
        type: string
      scopes:
        type: array
        items:
          type: string
        default: [ ]
      token_expiry_date:
        type: string
      access_token_name:
        type: string
        default: "access_token"
      expires_in_name:
        type: string
        default: "expires_in"
      refresh_request_body:
        type: object
      grant_type:
        type: string
        default: "refresh_token"
```

Example:

```yaml
authenticator:
  type: "OAuthAuthenticator"
  token_refresh_endpoint: "https://api.searchmetrics.com/v4/token"
  client_id: "{{ config['api_key'] }}"
  client_secret: "{{ config['client_secret'] }}"
  refresh_token: ""
```

## More readings

- [Requester](./requester.md)
- [Request options](./request-options.md)
