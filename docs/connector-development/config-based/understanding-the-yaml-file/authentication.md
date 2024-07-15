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
    "$parameters":
      "$ref": "#/definitions/$parameters"
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

The `BearerAuthenticator` is a specialized `ApiKeyAuthenticator` that always sets the header "Authorization" with the value `Bearer {token}`.
The following definition will set the header "Authorization" with a value "Bearer hello"

Schema:

```yaml
BearerAuthenticator:
  type: object
  additionalProperties: true
  required:
    - api_token
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
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
The following definition will set the header "Authorization" with a value `Basic {encoded credentials}`

Schema:

```yaml
BasicHttpAuthenticator:
  type: object
  additionalProperties: true
  required:
    - username
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
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
    "$parameters":
      "$ref": "#/definitions/$parameters"
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
      default: []
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

### JWT Authenticator

JSON Web Token (JWT) authentication is supported through the `JwtAuthenticator`.

Schema

```yaml
JwtAuthenticator:
  title: JWT Authenticator
  description: Authenticator for requests using JWT authentication flow.
  type: object
  required:
    - type
    - secret_key
    - algorithm
  properties:
    type:
      type: string
      enum: [JwtAuthenticator]
    secret_key:
      type: string
      description: Secret used to sign the JSON web token.
      examples:
        - "{{ config['secret_key'] }}"
    base64_encode_secret_key:
      type: boolean
      description: When set to true, the secret key will be base64 encoded prior to being encoded as part of the JWT. Only set to "true" when required by the API.
      default: False
    algorithm:
      type: string
      description: Algorithm used to sign the JSON web token.
      enum:
        [
          "HS256",
          "HS384",
          "HS512",
          "ES256",
          "ES256K",
          "ES384",
          "ES512",
          "RS256",
          "RS384",
          "RS512",
          "PS256",
          "PS384",
          "PS512",
          "EdDSA",
        ]
      examples:
        - ES256
        - HS256
        - RS256
        - "{{ config['algorithm'] }}"
    token_duration:
      type: integer
      title: Token Duration
      description: The amount of time in seconds a JWT token can be valid after being issued.
      default: 1200
      examples:
        - 1200
        - 3600
    header_prefix:
      type: string
      title: Header Prefix
      description: The prefix to be used within the Authentication header.
      examples:
        - "Bearer"
        - "Basic"
    jwt_headers:
      type: object
      title: JWT Headers
      description: JWT headers used when signing JSON web token.
      additionalProperties: false
      properties:
        kid:
          type: string
          title: Key Identifier
          description: Private key ID for user account.
          examples:
            - "{{ config['kid'] }}"
        typ:
          type: string
          title: Type
          description: The media type of the complete JWT.
          default: JWT
          examples:
            - JWT
        cty:
          type: string
          title: Content Type
          description: Content type of JWT header.
          examples:
            - JWT
    additional_jwt_headers:
      type: object
      title: Additional JWT Headers
      description: Additional headers to be included with the JWT headers object.
      additionalProperties: true
    jwt_payload:
      type: object
      title: JWT Payload
      description: JWT Payload used when signing JSON web token.
      additionalProperties: false
      properties:
        iss:
          type: string
          title: Issuer
          description: The user/principal that issued the JWT. Commonly a value unique to the user.
          examples:
            - "{{ config['iss'] }}"
        sub:
          type: string
          title: Subject
          description: The subject of the JWT. Commonly defined by the API.
        aud:
          type: string
          title: Audience
          description: The recipient that the JWT is intended for. Commonly defined by the API.
          examples:
            - "appstoreconnect-v1"
    additional_jwt_payload:
      type: object
      title: Additional JWT Payload Properties
      description: Additional properties to be added to the JWT payload.
      additionalProperties: true
    $parameters:
      type: object
      additionalProperties: true
```

Example:

```yaml
authenticator:
  type: JwtAuthenticator
  secret_key: "{{ config['secret_key'] }}"
  base64_encode_secret_key: True
  algorithm: RS256
  token_duration: 3600
  header_prefix: Bearer
  jwt_headers:
    kid: "{{ config['kid'] }}"
    cty: "JWT"
  additional_jwt_headers:
    test: "{{ config['test']}}"
  jwt_payload:
    iss: "{{ config['iss'] }}"
    sub: "sub value"
    aud: "aud value"
  additional_jwt_payload:
    test: "test custom payload"
```

## More readings

- [Requester](./requester.md)
- [Request options](./request-options.md)
