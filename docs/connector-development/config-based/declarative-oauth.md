---
title: Declarative OAuth (beta)
---

# Declarative OAuth

Declarative OAuth is a powerful feature that allows connector developers to implement OAuth authentication flows without writing any code. Instead of implementing custom OAuth logic, developers can describe their OAuth flow through configuration in their connector's spec file.

**Key Benefits:**
* **Zero Code Implementation** - Define your entire OAuth flow through configuration
* **Flexible & Customizable** - Handles both standard and non-standard OAuth implementations through custom parameters, headers, and URL templates
* **Standardized & Secure** - Uses Airbyte's battle-tested OAuth implementation
* **Maintainable** - OAuth configuration lives in one place and is easy to update

**When to Use:**
* You need to implement OAuth authentication for a new connector
* Your API uses standard OR custom OAuth 2.0 flows
* You want to refactor an existing custom OAuth implementation
* You need to customize OAuth parameters, headers, or URL structures

**How it Works:**
1. Developer defines OAuth configuration in connector spec
2. Airbyte handles OAuth flow coordination:
   * Generating consent URLs
   * Managing state parameters
   * Token exchange
   * Refresh token management
   * Custom parameter injection
   * Header management
3. Connector receives valid tokens for API authentication

The feature is configured through the `advanced_auth.oauth_config_specification` field in your connector's spec file, with most of the OAuth-specific configuration happening in the `oauth_connector_input_specification` subfield.

## Overview

In an ideal world, implementing OAuth 2.0 authentication for each data provider would be straightforward. The main pattern involves: `Consent Screen` > `Permission/Scopes Validation` > `Access Granted`. At Airbyte, we've refined various techniques to provide the best OAuth 2.0 experience for community developers.

Previously, each connector supporting OAuth 2.0 required a custom implementation, which was difficult to maintain, involved extensive testing, and was prone to issues when introducing breaking changes.

The modern solution is the `DeclarativeOAuthFlow`, which allows customers to configure, test, and maintain OAuth 2.0 using `JSON` or `YAML` configurations instead of extensive code.

Once the configuration is set, the `DeclarativeOAuthFlow` handles the following steps:
- Formats pre-defined URLs (including variable resolution)
- Displays the `Consent Screen` for permission/scope verification (depending on the data provider)
- Completes the flow by granting the `access_token`/`refresh_token` for authenticated API calls

## Implementation Examples

Let's walk through implementing OAuth flows of increasing complexity. Each example builds on the previous one.

**Base Connector Spec**
Here is an example of a manifest for a connector that
1. Has no existing Auth
2. Connects to the Pokemon API
3. Pulls data from the moves stream

```yaml
version: 6.13.0

type: DeclarativeSource

check:
  type: CheckStream
  stream_names:
    - moves

definitions:
  streams:
    moves:
      type: DeclarativeStream
      name: moves
      retriever:
        type: SimpleRetriever
        requester:
          $ref: "#/definitions/base_requester"
          path: /api/v2/move/
          http_method: GET
        record_selector:
          type: RecordSelector
          extractor:
            type: DpathExtractor
            field_path: []
        paginator:
          type: DefaultPaginator
          page_token_option:
            type: RequestPath
          pagination_strategy:
            type: CursorPagination
            cursor_value: "{{ response.get('next') }}"
            stop_condition: "{{ response.get('next') is none }}"
      schema_loader:
        type: InlineSchemaLoader
        schema:
          $ref: "#/schemas/moves"
  base_requester:
    type: HttpRequester
    url_base: https://pokeapi.co

streams:
  - $ref: "#/definitions/streams/moves"

spec:
  type: Spec
  connection_specification:
    type: object
    $schema: http://json-schema.org/draft-07/schema#
    required: []
    properties: {}
    additionalProperties: true

schemas:
  moves:
    type: object
    $schema: http://json-schema.org/schema#
    additionalProperties: true
    properties:
      count:
        type:
          - number
          - "null"
      next:
        type:
          - string
          - "null"
      previous:
        type:
          - string
          - "null"
      results:
        type:
          - array
          - "null"
        items:
          type:
            - object
            - "null"
          properties:
            name:
              type:
                - string
                - "null"
            url:
              type:
                - string
                - "null"


```

### Basic OAuth Flow
Lets update the spec to add a very basic OAuth flow with
1. No custom parameters
2. No custom headers
3. No custom query parameters
4. No refresh token support
5. No overrides to existing keys
6. No overrides to where we store or extract access tokens from
7. No overrides to where we store or extract client ids and secrets from

This service has two endpoints:
**Consent URL**
`/oauth/consent` - This is the consent URL that the user will be redirected to in order to authorize the connector

Example: `https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=https://cloud.airbyte.com&state=some_random_state_string`

**Token URL**
`/oauth/token` - This is the token URL that the connector will use to exchange the code for an access token

Example URL:
`https://yourconnectorservice.com/oauth/token?client_id=YOUR_CLIENT_ID_123&client_secret=YOUR_CLIENT_SECRET_123&code=some_random_code_string`

Example Response:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
}
```

#### Example Declarative OAuth Spec
```diff
--- manifest.yml
+++ simple_oauth_manifest.yml
definitions:
   base_requester:
     type: HttpRequester
     url_base: https://pokeapi.co
+    authenticator:
+      type: OAuthAuthenticator
+      refresh_request_body: {}
+      client_id: "{{ config[\"client_id\"] }}"
+      client_secret: "{{ config[\"client_secret\"] }}"
+      access_token_value: "{{ config[\"client_access_token\"] }}"

spec:
  connection_specification:
    type: object
    $schema: http://json-schema.org/draft-07/schema#
-    required: []
-    properties: {}
+    required:
+      - client_id
+      - client_secret
+      - client_access_token
+    properties:
+      client_id:
+        type: string
+      client_secret:
+        type: string
+      client_access_token:
+        type: string
+        airbyte_secret: true
     additionalProperties: true
+  advanced_auth:
+    auth_flow_type: oauth2.0
+    oauth_config_specification:
+      oauth_connector_input_specification:
+        consent_url: >-
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
+          redirect_uri_value}}&state={{state}}
+        access_token_url: >-
+          https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code {{auth_code_value}}
+      complete_oauth_output_specification:
+        required:
+          - access_token
+        properties:
+          access_token:
+            type: string
+            path_in_connector_config:
+              - access_token
+            path_in_oauth_response:
+              - access_token
+      complete_oauth_server_input_specification:
+        required:
+          - client_id
+          - client_secret
+        properties:
+          client_id:
+            type: string
+          client_secret:
+            type: string
+      complete_oauth_server_output_specification:
+        required:
+          - client_id
+          - client_secret
+        properties:
+          client_id:
+            type: string
+            path_in_connector_config:
+              - client_id
+          client_secret:
+            type: string
+            path_in_connector_config:
+              - client_secret

```

### Advanced Case: client secret is a request header not a query parameter
Imagine that the OAuth flow is updated so that the client secret is a request header instead of a query parameter.

#### Example Declarative OAuth Change
Here is the change you would make to the spec to support this:
```diff
--- simple_oauth_manifest.yml
+++ secret_header_manifest.yml
      spec:
        https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
        redirect_uri_value }}&state={{ state }}
        access_token_url: >-
-         https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+         https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&code={{auth_code_value}}
+       access_token_headers:
+         SECRETHEADER: "{{ client_secret_value }}"
       complete_oauth_output_specification:
         required:

```

#### Example with the header value encoded into `base64-string`
In this case, the header value would be encoded into `base64-encoded` string before being added to the headers.

Here is the change you would make to the spec to support this:
```diff
--- secret_header_manifest.yml
+++ secret_header_manifest.yml
      spec:
           https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
           redirect_uri_value }}&state={{ state }}
         access_token_url: >-
-          https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+          https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&code={{auth_code_value}}
+        access_token_headers:
-          SECRETHEADER: "{{ client_secret_value }}"
+          SECRETHEADER: "{{ {{client_id_value}}:{{client_secret_value}} | base64Encoder }}"
       complete_oauth_output_specification:
         required:

```

### Advanced Case: access token url query parameters should be `JSON-encoded`
Imagine that the OAuth flow is updated so that the query parameters should be `JSON-encoded` to obtain the `access_token/refresh_token`, during the `code` to `access_token/refresh_token` exchange. In this case the `access_token_url` should not include the variables as a part of the `url` itself. Use the `access_token_params` property to include the `JSON-encoded` params in the `body` of the request.

#### Example Declarative OAuth Change
Here is the change you would make to the spec to support this:
```diff
--- simple_oauth_manifest.yml
+++ secret_header_manifest.yml
      spec:
           https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
           redirect_uri_value }}&state={{ state }}
         access_token_url: >-
-          https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+          https://yourconnectorservice.com/oauth/token
+        access_token_params:
+          client_id: "{{ client_id_value }}"
+          client_secret: "{{ client_secret_value }}"
+          redirect_uri: "{{ redirect_uri_value }}"
       complete_oauth_output_specification:
         required:

```

The underlying `JSON-encoded` parameters will be included in the `body` of the outgoing request, instead of being a part of the `access_token_url` url value, as follows:
```json
{
   "client_id": "YOUR_CLIENT_ID_123",
   "client_secret": "YOUR_CLIENT_SECRET_123",
   "redirect_uri": "https://cloud.airbyte.com",
}

```

### Advanced Case: access token is returned in a non standard / nested field
Now imagine that the OAuth flow is updated so that the access token returned by `/oauth/token` is in a nested non standard field. Specifically, the response is now:
```json
{
  "data": {
    "super_duper_access_token": "YOUR_ACCESS_TOKEN_123"
  }
}
```

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ different_access_token_field.yml
    spec:
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
       complete_oauth_output_specification:
         required:
-          - access_token
+          - super_duper_access_token
         properties:
-          access_token:
+          super_duper_access_token:
             type: string
             path_in_connector_config:
               - access_token
+            path_in_oauth_response:
+              - data
+              - super_duper_access_token
       complete_oauth_server_input_specification:
```

### Advanced Case: refresh token / single-use refresh token support 
Imagine that the OAuth flow is updated so that the OAuth flow now supports refresh tokens.

Meaning that the OAuth flow now has an additional endpoint:
`/oauth/refresh` - This is the refresh token URL that the connector will use to exchange the refresh token for an access token

Example URL: https://yourconnectorservice.com/oauth/refresh/endpoint

and the response of `/oauth/token` now includes a refresh token field.
```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123",
  "expires_in": 7200,
}
```

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ refresh_token.yml
  definitions:
     authenticator:
       type: OAuthAuthenticator
       refresh_request_body: {}
+      grant_type: refresh_token
       client_id: "{{ config[\"client_id\"] }}"
       client_secret: "{{ config[\"client_secret\"] }}"
+      refresh_token: "{{ config[\"client_refresh_token\"] }}"
       access_token_value: "{{ config[\"client_access_token\"] }}"
+      access_token_name: access_token
+      refresh_token_updater:
+        refresh_token_name: refresh_token
+        refresh_token_config_path:
+          - client_refresh_token
+      token_refresh_endpoint: >-
+        https://yourconnectorservice.com/oauth/refresh/endpoint

 streams:
   - $ref: "#/definitions/streams/moves"
 spec:
    required:
      - client_id
      - client_secret
-     - client_access_token
+     - client_refresh_token
     properties:
       client_id:
         type: string
@@ -68,9 +77,9 @@ spec:
-      client_access_token:
+      client_refresh_token:
         type: string
-        title: Access token
+        title: Refresh token
@@ -86,16 +95,22 @@ spec:
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}           
       complete_oauth_output_specification:
         required:
           - access_token
+          - refresh_token
+          - token_expiry_date
         properties:
           access_token:
             type: string
             path_in_connector_config:
               - access_token
+            path_in_oauth_response:
+              - access_token
+          refresh_token:
+            type: string
+            path_in_connector_config:
+              - refresh_token
+            path_in_oauth_response:
+              - refresh_token
+          token_expiry_date:
+            type: string
+            path_in_connector_config:
+              - token_expiry_date
+            path_in_oauth_response:
+              - expires_in
       complete_oauth_server_input_specification:
         required:
           - client_id

```

### Advanced Case: scopes should be provided as a query parameter 
Imagine that the OAuth flow is updated so that you need to mention the `scope` query parameter to get to the `consent screen` and verify / grant the access to the neccessary onces, before moving forward.

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ scopes.yml
@@ -80,10 +80,10 @@ spec:
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
-          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
-          redirect_uri_value }}&state={{ state_value }}
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{ redirect_uri_value }}&state={{ state_value }}&scope={{scope_value}}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+        scope: my_scope_A:read,my_scope_B:read
       complete_oauth_output_specification:
         required:
           - access_token

```

### Advanced Case: generate the complex `state` value and make it a part of the query parameter 
Imagine that the OAuth flow is updated so that you need to mention the `state` query parameter being generated with the minimum `10` and maximum `27` symbols.

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ base_oauth_with_custom_state.yml
@@ -80,10 +80,10 @@ spec:
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
           https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
           redirect_uri_value }}&state={{ state_value }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+        state: {
+          min: 10,
+          max: 27
+        }
       complete_oauth_output_specification:
         required:
           - access_token

```

Example URL:
`https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=https://cloud.airbyte.com&state=2LtdNpN8pmkYOBDqoVR3NzYQ`

#### Example using an url-encoded / url-decoded `scope` parameter
You can make the `scope` paramter `url-encoded` by specifying the `pipe` ( | ) + `urlEncoder` or `urlDecoder` in the target url.
It would be pre-formatted and resolved into the `url-encoded` string before being replaced for the final resolved URL. 

```diff
--- scopes.yml
+++ scopes.yml
@@ -80,10 +80,10 @@ spec:
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
-          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
-          redirect_uri_value }}&state={{ state_value }}&scope={{scope_value}}
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{ redirect_uri_value }}&state={{ state_value }}&scope={{ {{scope_value}} | urlEncoder }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
-        scope: my_scope_A:read,my_scope_B:read
+        scope: my_scope_A:read my_scope_B:read
       complete_oauth_output_specification:
         required:
           - access_token

```

Example URL:
`https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=https://cloud.airbyte.com&state=some_random_state_string&scope=my_scope_A%3Aread%20my_scope_B%3Aread`


### Advanced Case: get code challenge from the `state_value` and set as a part of the `consent_url` 
Imagine that the OAuth flow is updated so that you need to generate the `code challenge`, using `SHA-256` hash and include this as a query parameter in the `consent_url` to get to the `Consent Screen`, before moving forward with authentication.

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ base_oauth.yml
  spec:
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
-          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
-          redirect_uri_value }}&state={{ state_value }}
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
+          redirect_uri_value }}&state={{ state_value }}&code_challenge={{ {{state_value}} | codeChallengeS256 }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
       complete_oauth_output_specification:
         required:
           - access_token

```


### Advanced Case: The Connector is already using Legacy OAuth and the credentials are stored in a strange place
Imagine that the connector is already using Legacy OAuth and the credentials are stored in a strange place.

Specifically:
1. `client_id` is located in a users config file at `airbyte.super_secret_credentials.pokemon_client_id`
2. `client_secret` is located in a users config file at `airbyte.super_secret_credentials.pokemon_client_secret`
3. `access_token` is located in a users config file at `airbyte.super_secret_credentials.pokemon_access_token`

and we need to make sure that updating the spec to use Declarative OAuth doesn't break existing syncs.

#### Example Declarative OAuth Change
```diff
--- base_oauth.yml
+++ legacy_to_declarative_oauth.yml
  definitions:
     authenticator:
       type: OAuthAuthenticator
       refresh_request_body: {}
-      client_id: '{{ config["client_id"] }}'
-      client_secret: '{{ config["client_secret"] }}'
-      access_token_value: '{{ config["client_access_token"] }}'
+      client_id: '{{ config["super_secret_credentials"]["pokemon_client_id"] }}'
+      client_secret: '{{ config["super_secret_credentials"]["pokemon_client_secret"] }}'
+      access_token_value: '{{ config["super_secret_credentials"]["pokemon_access_token"] }}'
 
 streams:
   - $ref: "#/definitions/streams/moves"
 spec:
     type: object
     $schema: http://json-schema.org/draft-07/schema#
     required:
-      - client_id
-      - client_secret
-      - client_access_token
+      - super_secret_credentials
     properties:
-      client_id:
-        type: string
-        title: Client ID
-        airbyte_secret: true
-        order: 0
-      client_secret:
-        type: string
-        title: Client secret
-        airbyte_secret: true
-        order: 1
-      client_access_token:
-        type: string
-        title: Access token
-        airbyte_secret: true
-        airbyte_hidden: false
-        order: 2
+      super_secret_credentials:
+        required:
+          - pokemon_client_id
+          - pokemon_client_secret
+          - pokemon_access_token
+        pokemon_client_id:
+          type: string
+          title: Client ID
+          airbyte_secret: true
+          order: 0
+        pokemon_client_secret:
+          type: string
+          title: Client secret
+          airbyte_secret: true
+          order: 1
+        pokemon_access_token:
+          type: string
+          title: Access token
+          airbyte_secret: true
+          airbyte_hidden: false
+          order: 2
     additionalProperties: true
   advanced_auth:
     auth_flow_type: oauth2.0
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
-          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
-          redirect_uri_value }}&state={{ state_value }}
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{ redirect_uri_value }}&state={{ s
tate_value }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_
code_value}}
+        client_id_key: pokemon_client_id
+        client_secret_key: pokemon_client_secret
       complete_oauth_output_specification:
         required:
-          - access_token
+          - pokemon_access_token
         properties:
          access_token:
             type: string
             path_in_connector_config:
-              - access_token
+              - super_secret_credentials
+              - pokemon_access_token
             path_in_oauth_response:
               - access_token
       complete_oauth_server_input_specification:
         required:
-          - client_id
-          - client_secret
+          - pokemon_client_id
+          - pokemon_client_secret
         properties:
-          client_id:
+          pokemon_client_id:
             type: string
-          client_secret:
+          pokemon_client_secret:
             type: string
       complete_oauth_server_output_specification:
         required:
-          - client_id
-          - client_secret
+          - pokemon_client_id
+          - pokemon_client_secret
         properties:
-          client_id:
+          pokemon_client_id:
             type: string
             path_in_connector_config:
-              - client_id
-          client_secret:
+              - super_secret_credentials
+              - pokemon_client_id
+          pokemon_client_secret:
             type: string
             path_in_connector_config:
-              - client_secret
+              - super_secret_credentials
+              - pokemon_client_secret

```


## Configuration Fields

### Required Fields

| Field | Description | Default Value |
|-------|-------------|---------------|
| `consent_url` | The URL where the user will be redirected to authorize the connector | NA |
| `access_token_url` | The URL where the connector will exchange the authorization code for an access token | NA |


### Optional Fields

| Field | Description | Default Value |
|-------|-------------|---------------|
| `access_token_headers` | The optional headers to inject while exchanging the `auth_code` to `access_token` | NA |
| `access_token_params` | The optional query parameters to inject while exchanging the `auth_code` to `access_token` | NA |
| `auth_code_key` | The optional override to provide the custom `code` key name to something like `auth_code` or `custom_auth_code`, if required by data-provider  | "code" |
| `client_id_key` | The optional override to provide the custom `client_id` key name, if required by data-provider  | "client_id" |
| `client_secret_key` | The optional override to provide the custom `client_secret` key name, if required by data-provider  | "client_secret" |
| `redirect_uri_key` | The optional override to provide the custom `redirect_uri` key name to something like `callback_uri`, if required by data-provider  | "redirect_uri" |
| `scope` | The optional string of the scopes needed to be grant for authenticated user, should be pre-defined as a `string` in a format that is expected by the data-provider  | NA |
| `scope_key` | The optional override to provide the custom `scope` key name, if required by data-provider  | "scope" |
| `state` | The object to provide the criteria of how the `state` query param should be constructed, including length and complexity | NA |
| `state_key` | The optional override to provide the custom `state` key name, if required by data-provider  | "state" |
| `token_expiry_key` | The optional override to provide the custom key name to something like `expires_at`, if required by data-provider  | "expires_in" |

## Available Template Variables
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `{{ client_id_key }}` | The key used to identify the client ID in request bodies | "client_id" |
| `{{ client_id_value }}` | The client ID value retrieved from the config location specified by client_id_key | Value from config[client_id_key] |
| `{{ client_id_param }}` | The parameter name and value pair used for the client ID in URLs | "client_id=client id value here" |
| `{{ client_secret_key }}` | The key used to identify the client secret in request bodies | "client_secret" |
| `{{ client_secret_value }}` | The client secret value retrieved from the config location specified by client_secret_key | Value from config[client_secret_key] |
| `{{ client_secret_param }}` | The parameter name and value pair used for the client secret in URLs | "client_secret=client secret value here" |
| `{{ redirect_uri_key }}` | The key used to identify the redirect URI in request bodies | "redirect_uri" |
| `{{ redirect_uri_value }}` | The redirect URI value used for OAuth callbacks | Value configured in Airbyte |
| `{{ redirect_uri_param }}` | The parameter name and value pair used for the redirect URI in URLs | "redirect_uri=redirect uri value here" |
| `{{ scope_key }}` | The key used to identify the scope in request bodies | "scope" |
| `{{ scope_value }}` | The scope value specifying the access permissions being requested | Value from config[scope_key] |
| `{{ scope_param }}` | The parameter name and value pair used for the scope in URLs | "scope=scope value here" |
| `{{ state_key }}` | The key used to identify the state parameter in request bodies | "state" |
| `{{ state_value }}` | A random string used to prevent CSRF attacks | Randomly generated string |
| `{{ state_param }}` | The parameter name and value pair used for the state in URLs | "state=state value here" |
| `{{ auth_code_key }}` | The key used to identify the authorization code in request bodies | "code" |
| `{{ auth_code_value }}` | The authorization code received from the OAuth provider | Value from OAuth callback |
| `{{ auth_code_param }}` | The parameter name and value pair used for the auth code in URLs | "code=auth code value here" |

## Available Template Variables PIPE methods

You can apply the 

| Method | Description | Input Value | Output Value |
|----------|-------------|------|------|
| `base64Encoder` | The variable method to encode the input string into `base64-encoded` string | "client_id_123:client_secret_456" | "Y2xpZW50X2lkXzEyMzpjbGllbnRfc2VjcmV0XzQ1Ng" |
| `base64Encoder` | The variable method to decode the `base64-encoded` input string into `base64-decoded` string | "Y2xpZW50X2lkXzEyMzpjbGllbnRfc2VjcmV0XzQ1Ng" | "client_id_123:client_secret_456" |
| `codeChallengeS256` | The variable method to encode the input string into `SHA-256` hashed-string | "id_123:secret_456" | "kdlBQTTftIOzHnzQoqp3dQ5jBsSehFTjg1meg1gL3OY" |
| `urlEncoder` | The variable method to encode the input string as `URL-string` | "my string input" | "my%20string%20input" |
| `urlDecoder` | The variable method to decode the input `URL-string` into decoded string | "my%20string%20input" | "my string input" |


## More scenarious examples:
The following section stands to describe common use-cases. Assuming that there are no overides provided over the `default` keys, the common specification parts (properties) like: `complete_oauth_server_input_specification` and `complete_oauth_server_output_specification` remain unchanged

```yaml
complete_oauth_server_input_specification:
  required:
    - client_id
    - client_secret
  properties:
    client_id:
      type: string
    client_secret:
      type: string
complete_oauth_server_output_specification:
  required:
    - client_id
    - client_secret
  properties:
    client_id:
      type: string
      path_in_connector_config:
        - client_id
    client_secret:
      type: string
      path_in_connector_config:
        - client_secret
```

### Case A: OAuth Flow returns the `access_token` only
When the `access_token` is the only key expected after the successfull `OAuth2.0` authentication

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - access_token
    properties:
      access_token:
        type: string
        path_in_connector_config:
          - access_token
        path_in_oauth_response:
          - access_token
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123"
}
```

#### Case A-1: OAuth Flow returns the nested `access_token` only, under the `data` property

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - access_token
    properties:
      access_token:
        type: string
        path_in_connector_config:
          - access_token
        path_in_oauth_response:
          - data
          - access_token
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "data": {
    "access_token": "YOUR_ACCESS_TOKEN_123"
  }
}
```

### Case B: OAuth Flow returns the `refresh_token` only
When the `refresh_token` is the only key expected after the successfull `OAuth2.0` authentication

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - refresh_token
    properties:
      refresh_token:
        type: string
        path_in_connector_config:
          - refresh_token
        path_in_oauth_response:
          - refresh_token
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "refresh_token": "YOUR_ACCESS_TOKEN_123"
}
```

### Case C: OAuth Flow returns the `access_token` and the `refresh_token`
When the the `access_token` and the `refresh_token` are the only keys expected after the successfull `OAuth2.0` authentication

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - access_token
      - refresh_token
    properties:
      access_token:
        type: string
        path_in_connector_config:
          - access_token
        path_in_oauth_response:
          - access_token
      refresh_token:
        type: string
        path_in_connector_config:
          - refresh_token
        path_in_oauth_response:
          - refresh_token
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123"
}
```

#### Case C-1: OAuth Flow returns the `access_token` and the `refresh_token` nested under the `data` property and each key is nested inside the dedicated placeholder

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - access_token
      - refresh_token
    properties:
      access_token:
        type: string
        path_in_connector_config:
          - access_token
        path_in_oauth_response:
          - data
          - access_token_placeholder
          - access_token
      refresh_token:
        type: string
        path_in_connector_config:
          - refresh_token
        path_in_oauth_response:
          - data
          - refresh_token_placeholder
          - refresh_token
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "data": {
    "access_token_placeholder": {
      "access_token": "YOUR_ACCESS_TOKEN_123"
    },
    "refresh_token_placeholder" {
      "refresh_token": "YOUR_REFRESH_TOKEN_123"
    }
  }
}
```

### Case D: OAuth Flow returns the `access_token` and the `refresh_token` is a `single-use` key 
In this example we expect the `refresh_token` key expires alongside with the `access_token` and should be exhanged alltogher, having the new pair of keys in response. The `token_expiry_date` is the property that holds the `date-time` value of when the `access_token` should be expired.

```yaml
# advanced_auth

oauth_config_specification:
  oauth_connector_input_specification:
    consent_url: >-
      https://yourconnectorservice.com/oauth/consent?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}
    access_token_url: >-
      https://yourconnectorservice.com/oauth/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}
  complete_oauth_output_specification:
    required:
      - access_token
      - refresh_token
      - token_expiry_date
    properties:
      access_token:
        type: string
        path_in_connector_config:
          - access_token
        path_in_oauth_response:
          - access_token
      refresh_token:
        type: string
        path_in_connector_config:
          - refresh_token
        path_in_oauth_response:
          - refresh_token
      token_expiry_date:
        type: string
        path_in_connector_config:
          - token_expiry_date
        path_in_oauth_response:
          - expires_in
  
  # Other common properties are omitted, see the `More scenarious examples` description
```
The `path_in_oauth_response` looks like:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123",
  "expires_in": 7200
}
```