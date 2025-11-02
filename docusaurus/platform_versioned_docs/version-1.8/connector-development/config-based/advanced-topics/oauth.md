# OAuth Authentication Methods
At Aribyte, we offer two options for authentication using `OAuth2.0`:

1. **Airbyte's Own OAuth Application**: With this option, you do not need to create your own OAuth application with the data provider. This is typically applied to `Airbyte Cloud` customers as a `pick-and-use` scenario.
2. **Declarative OAuth2.0**: This option requires you to provide your own `client id` and `client secret` (parameters may vary based on the data provider's preferences). You will need to supply the configuration, which will be processed and executed by the Airbyte platform on your behalf (self-managed configuration).


## Declarative OAuth 2.0

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

### Overview

In an ideal world, implementing OAuth 2.0 authentication for each data provider would be straightforward. The main pattern involves: `Consent Screen` > `Permission/Scopes Validation` > `Access Granted`. At Airbyte, we've refined various techniques to provide the best OAuth 2.0 experience for community developers.

Previously, each connector supporting OAuth 2.0 required a custom implementation, which was difficult to maintain, involved extensive testing, and was prone to issues when introducing breaking changes.

The modern solution is the `DeclarativeOAuthFlow`, which allows customers to configure, test, and maintain OAuth 2.0 using `JSON` or `YAML` configurations instead of extensive code.

Once the configuration is set, the `DeclarativeOAuthFlow` handles the following steps:
- Formats pre-defined URLs (including variable resolution)
- Displays the `Consent Screen` for permission/scope verification (depending on the data provider)
- Completes the flow by granting the `access_token`/`refresh_token` for authenticated API calls

### Implementation Examples

Let's walk through implementing OAuth flows of increasing complexity. Each example builds on the previous one.

**Base Connector Spec**
Here is an example of a manifest for a connector that
1. Has no existing Auth
2. Connects to the Pokemon API
3. Pulls data from the moves stream

<details>
  <summary>Example Base Connector Spec</summary>

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
</details>


#### Basic OAuth Flow
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

  <details>
    <summary>Example Response</summary>

  ```json
  {
    "access_token": "YOUR_ACCESS_TOKEN_123"
  }
  ```
  </details>

  <details>
    <summary>Example Declarative OAuth Spec</summary>

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
  </details>

#### Advanced Case: client secret is a request header not a query parameter
Imagine that the OAuth flow is updated so that the client secret is a request header instead of a query parameter.

  <details>
    <summary>Example Declarative OAuth Change</summary>

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
  </details>

  <details>
    <summary>Example with the header value encoded into `base64-string`</summary>

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
+          SECRETHEADER: "{{ (client_id_value ~ ':' ~ client_secret_value) | b64encode }}"
       complete_oauth_output_specification:
         required:
```
  </details>


#### Advanced Case: access token url query parameters should be `JSON-encoded`
Imagine that the OAuth flow is updated so that the query parameters should be `JSON-encoded` to obtain the `access_token/refresh_token`, during the `code` to `access_token/refresh_token` exchange. In this case the `access_token_url` should not include the variables as a part of the `url` itself. Use the `access_token_params` property to include the `JSON-encoded` params in the `body` of the request.

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>

The underlying `JSON-encoded` parameters will be included in the `body` of the outgoing request, instead of being a part of the `access_token_url` url value, as follows:

  <details>
      <summary>Example rendered `access_token_params`</summary>

```json
{
  "client_id": "YOUR_CLIENT_ID_123",
  "client_secret": "YOUR_CLIENT_SECRET_123",
  "redirect_uri": "https://cloud.airbyte.com",
}
```
  </details>


#### Advanced Case: access token is returned in a non standard / nested field
Now imagine that the OAuth flow is updated so that the access token returned by `/oauth/token` is in a nested non standard field. Specifically, the response is now:

  <details>
      <summary>Example response</summary>

```json
{
  "data": {
    "super_duper_access_token": "YOUR_ACCESS_TOKEN_123"
  }
}
```
  </details>

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>

#### Advanced Case: refresh token / single-use refresh token support
Imagine that the OAuth flow is updated so that the OAuth flow now supports refresh tokens.

Meaning that the OAuth flow now has an additional endpoint:
`/oauth/refresh` - This is the refresh token URL that the connector will use to exchange the refresh token for an access token

  <details>
      <summary>Example URL</summary>

`https://yourconnectorservice.com/oauth/refresh/endpoint`
  </details>

and the response of `/oauth/token` now includes a refresh token field.

  <details>
      <summary>Example response</summary>

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123",
  "expires_in": 7200,
}
```
  </details>

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>

#### Advanced Case: scopes should be provided as a query parameter
Imagine that the OAuth flow is updated so that you need to mention the `scope` query parameter to get to the `consent screen` and verify / grant the access to the neccessary onces, before moving forward.

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>

#### Advanced Case: generate the complex `state` value and make it a part of the query parameter
Imagine that the OAuth flow is updated so that you need to mention the `state` query parameter being generated with the minimum `10` and maximum `27` symbols.

  <details>
      <summary>Example URL</summary>

`https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=https://cloud.airbyte.com&state=2LtdNpN8pmkYOBDqoVR3NzYQ`

  </details>

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>


##### Example using an url-encoded / url-decoded `scope` parameter
You can make the `scope` paramter `url-encoded` by specifying the `pipe` ( | ) + `urlencode` or `urldecode` in the target url.
It would be pre-formatted and resolved into the `url-encoded` string before being replaced for the final resolved URL.

  <details>
      <summary>Example URL</summary>

`https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=https://cloud.airbyte.com&state=some_random_state_string&scope=my_scope_A%3Aread%20my_scope_B%3Aread`
  </details>

  <details>
      <summary>Example Declarative OAuth Change</summary>

```diff
--- scopes.yml
+++ scopes.yml
@@ -80,10 +80,10 @@ spec:
     oauth_config_specification:
       oauth_connector_input_specification:
         consent_url: >-
-          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{
-          redirect_uri_value }}&state={{ state_value }}&scope={{scope_value}}
+          https://yourconnectorservice.com/oauth/consent?client_id={{client_id_value}}&redirect_uri={{ redirect_uri_value }}&state={{ state_value }}&scope={{ scope_value | urlencode }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
-        scope: my_scope_A:read,my_scope_B:read
+        scope: my_scope_A:read my_scope_B:read
       complete_oauth_output_specification:
         required:
           - access_token
```
  </details>


#### Advanced Case: get code challenge from the `state_value` and set as a part of the `consent_url`
Imagine that the OAuth flow is updated so that you need to generate the `code challenge`, using `SHA-256` hash and include this as a query parameter in the `consent_url` to get to the `Consent Screen`, before moving forward with authentication.

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
+          redirect_uri_value }}&state={{ state_value }}&code_challenge={{ state_value | codechallengeS256 }}
         access_token_url: >-
           https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
       complete_oauth_output_specification:
         required:
           - access_token
```
  </details>

#### Advanced Case: The Connector is already using Legacy OAuth and the credentials are stored in a strange place
Imagine that the connector is already using Legacy OAuth and the credentials are stored in a strange place.

Specifically:
1. `client_id` is located in a users config file at `airbyte.super_secret_credentials.pokemon_client_id`
2. `client_secret` is located in a users config file at `airbyte.super_secret_credentials.pokemon_client_secret`
3. `access_token` is located in a users config file at `airbyte.super_secret_credentials.pokemon_access_token`

and we need to make sure that updating the spec to use Declarative OAuth doesn't break existing syncs.

  <details>
      <summary>Example Declarative OAuth Change</summary>

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
  </details>

### Configuration Fields

#### Required Fields

| Field | Description | Default Value |
|-------|-------------|---------------|
| `consent_url` | The URL where the user will be redirected to authorize the connector |  |
| `access_token_url` | The URL where the connector will exchange the authorization code for an access token |  |


#### Optional Fields

| Field | Description | Default Value |
|-------|-------------|---------------|
| `access_token_headers` | The optional headers to inject while exchanging the `auth_code` to `access_token` |  |
| `access_token_params` | The optional query parameters to inject while exchanging the `auth_code` to `access_token` |  |
| `auth_code_key` | The optional override to provide the custom `code` key name to something like `auth_code` or `custom_auth_code`, if required by data-provider  | "code" |
| `client_id_key` | The optional override to provide the custom `client_id` key name, if required by data-provider  | "client_id" |
| `client_secret_key` | The optional override to provide the custom `client_secret` key name, if required by data-provider  | "client_secret" |
| `redirect_uri_key` | The optional override to provide the custom `redirect_uri` key name to something like `callback_uri`, if required by data-provider  | "redirect_uri" |
| `scope` | The optional string of the scopes needed to be grant for authenticated user, should be pre-defined as a `string` in a format that is expected by the data-provider  |  |
| `scope_key` | The optional override to provide the custom `scope` key name, if required by data-provider  | "scope" |
| `state` | The object to provide the criteria of how the `state` query param should be constructed, including length and complexity |  |
| `state_key` | The optional override to provide the custom `state` key name, if required by data-provider  | "state" |
| `token_expiry_key` | The optional override to provide the custom key name to something like `expires_at`, if required by data-provider  | "expires_in" |

### Available Template Variables
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `{{ client_id_key }}` | The key used to identify the client ID in request bodies | "client_id" |
| `{{ client_id_value }}` | The client ID value retrieved from the config location specified by client_id_key | Value from config[client_id_key] |
| `{{ client_id_param }}` | The parameter name and value pair used for the client ID in URLs | "client_id=client id value here" |
| `{{ client_secret_key }}` | The key used to identify the client secret in request bodies | "client_secret" |
| `{{ client_secret_value }}` | The client secret value retrieved from the config location specified by client_secret_key | Value from config[client_secret_key] |
| `{{ client_secret_param }}` | The parameter name and value pair used for the client secret in URLs | "client_secret=client secret value here" |
| `{{ redirect_uri_key }}` | The key used to identify the redirect URI in request bodies | "redirect_uri" |
| `{{ redirect_uri_value }}` | The redirect URI value used for OAuth callbacks | This value is set based on your deployment and handled by Airbyte |
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

### Available Template Variables PIPE methods

You can apply the `in-variable` tranformations based on your use-case and use the following interpolation methods available:

#### Most useful interpolation methods used for OAuth

| Name              | Description                                    | Example Input                                      | Example Output                                                                 |
|-------------------|------------------------------------------------|----------------------------------------------------|--------------------------------------------------------------------------------|
| urlencode         | URL-encodes a string.                          | `{{ 'hello world'\|urlencode }}`                   | `'hello%20world'`                                                           |
| urldecode         | URL-decodes a string.                          | `{{ 'hello%20world'\|urlencode }}`                 | `'hello world'`                                                           |
| b64encode         | Encodes a string using Base64.                 | `{{ 'hello'\|b64encode }}`                         | `aGVsbG8=`                                                                     |
| b64decode         | Decodes a Base64 encoded string.               | `{{ 'aGVsbG8='\|b64decode }}`                      | `hello`                                                                        |
| codechallengeS256 | Encodes the input string using `base64` + `SHA-256`. | `{{ 'id_123:secret_456'\|codechallengeS256 }}` | `kdlBQTTftIOzHnzQoqp3dQ5jBsSehFTjg1meg1gL3OY` |

#### Commonly used `Jinja2` in-variables interpolation methods available (the list is not exhaustive)

| Name              | Description                                    | Example Input                                      | Example Output                                                                 |
|-------------------|------------------------------------------------|----------------------------------------------------|--------------------------------------------------------------------------------|
| abs             | Returns the absolute value of a number.        | `{{ -3\|abs }}`                                    | `3`                                                                            |
| batch           | Batches items.                                 | `{{ [1, 2, 3, 4, 5, 6]\|batch(2) }}`              | `[[1, 2], [3, 4], [5, 6]]`                                                     |
| capitalize      | Capitalizes a string.                          | `{{ 'hello'\|capitalize }}`                        | `Hello`                                                                        |
| center          | Centers a string.                              | `{{ 'hello'\|center(9) }}`                         | `'  hello  '`                                                                  |
| default         | Returns the default value if undefined.        | `{{ undefined_variable\|default('default') }}`     | `default`                                                                      |
| dictsort        | Sorts a dictionary.                            | `{{ {'b': 1, 'a': 2}\|dictsort }}`                 | `{'a': 2, 'b': 1}`                                                             |
| escape          | Escapes a string.                              | `{{ '<div>'\|escape }}`                           | `&lt;div&gt;`                                                                  |
| filesizeformat  | Formats a number as a file size.               | `{{ 123456789\|filesizeformat }}`                  | `117.7 MB`                                                                     |
| first           | Returns the first item of a sequence.          | `{{ [1, 2, 3]\|first }}`                           | `1`                                                                            |
| float           | Converts a value to a float.                   | `{{ '42'\|float }}`                               | `42.0`                                                                         |
| forceescape     | Forces escaping of a string.                   | `{{ '<div>'\|forceescape }}`                      | `&lt;div&gt;`                                                                  |
| format          | Formats a string.                              | `{{ 'Hello %s'\|format('world') }}`                | `Hello world`                                                                  |
| groupby         | Groups items by a common attribute.            | `{{ [{'name': 'a'}, {'name': 'b'}]\|groupby('name') }}` | `{'a': [{'name': 'a'}], 'b': [{'name': 'b'}]}`                               |
| indent          | Indents a string.                              | `{{ 'hello'\|indent(4) }}`                         | `'    hello'`                                                                  |
| int             | Converts a value to an integer.                | `{{ '42'\|int }}`                                 | `42`                                                                           |
| join            | Joins a sequence of strings.                   | `{{ ['a', 'b', 'c']\|join(', ') }}`                | `'a, b, c'`                                                                    |
| last            | Returns the last item of a sequence.           | `{{ [1, 2, 3]\|last }}`                            | `3`                                                                            |
| length          | Returns the length of a sequence.              | `{{ [1, 2, 3]\|length }}`                          | `3`                                                                            |
| list            | Converts a value to a list.                    | `{{ 'abc'\|list }}`                               | `['a', 'b', 'c']`                                                              |
| lower           | Converts a string to lowercase.                | `{{ 'HELLO'\|lower }}`                            | `'hello'`                                                                      |
| map             | Applies a filter to a sequence of objects.     | `{{ [{'name': 'a'}, {'name': 'b'}]\|map(attribute='name') }}` | `['a', 'b']`                                                       |
| max             | Returns the maximum value of a sequence.       | `{{ [1, 2, 3]\|max }}`                             | `3`                                                                            |
| min             | Returns the minimum value of a sequence.       | `{{ [1, 2, 3]\|min }}`                             | `1`                                                                            |
| random          | Returns a random item from a sequence.         | `{{ [1, 2, 3]\|random }}`                          | `2`                                                                            |
| replace         | Replaces occurrences of a substring.           | `{{ 'hello'\|replace('l', 'x') }}`                 | `'hexxo'`                                                                      |
| reverse         | Reverses a sequence.                           | `{{ [1, 2, 3]\|reverse }}`                         | `[3, 2, 1]`                                                                    |
| round           | Rounds a number.                               | `{{ 2.7\|round }}`                                | `3`                                                                            |
| safe            | Marks a string as safe.                        | `{{ '<div>'\|safe }}`                             | `<div>`                                                                        |
| slice           | Slices a sequence.                             | `{{ [1, 2, 3, 4]\|slice(2) }}`                     | `[[1, 2], [3, 4]]`                                                             |
| sort            | Sorts a sequence.                              | `{{ [3, 2, 1]\|sort }}`                            | `[1, 2, 3]`                                                                    |
| string          | Converts a value to a string.                  | `{{ 42\|string }}`                                | `'42'`                                                                         |
| striptags       | Strips HTML tags from a string.                | `{{ '<div>hello</div>'\|striptags }}`              | `'hello'`                                                                      |
| sum             | Sums a sequence of numbers.                    | `{{ [1, 2, 3]\|sum }}`                             | `6`                                                                            |
| title           | Converts a string to title case.               | `{{ 'hello world'\|title }}`                       | `'Hello World'`                                                                |
| trim            | Trims whitespace from a string.                | `{{ '  hello  '\|trim }}`                          | `'hello'`                                                                      |
| truncate        | Truncates a string.                            | `{{ 'hello world'\|truncate(5) }}`                 | `'hello...'`                                                                |
| unique          | Returns unique items from a sequence.          | `{{ [1, 2, 2, 3]\|unique }}`                       | `[1, 2, 3]`                                                                 |
| upper           | Converts a string to uppercase.                | `{{ 'hello'\|upper }}`                            | `'HELLO'`                                                                    |
| urlize          | Converts URLs in a string to clickable links.  | `{{ 'Check this out: http://example.com'\|urlize }}` | `'Check this out: <a href="http://example.com">http://example.com</a>'`   |
| wordcount       | Counts the words in a string.                  | `{{ 'hello world'\|wordcount }}`                   | `2`                                                                            |
| wordwrap        | Wraps words in a string.                       | `{{ 'hello world'\|wordwrap(5) }}`                 | `'hello\nworld'`                                                               |
| xmlattr         | Creates an XML attribute string.               | `{{ {'class': 'my-class', 'id': 'my-id'}\|xmlattr }}` | `'class="my-class" id="my-id"'`                                                |
| dateformat      | Formats a date.                                | `{{ date\|dateformat('%Y-%m-%d') }}`               | `'2023-10-01'`                                                                 |
| datetimeformat  | Formats a datetime.                            | `{{ datetime\|datetimeformat('%Y-%m-%d %H:%M:%S') }}` | `'2023-10-01 12:00:00'`                                                        |
| time            | Formats a time.                                | `{{ time\|time('%H:%M:%S') }}`                     | `'12:00:00'`                                                                   |
| timesince       | Returns the time since a date.                 | `{{ date\|timesince }}`                            | `'2 days ago'`                                                                 |
| timeuntil       | Returns the time until a date.                 | `{{ date\|timeuntil }}`                            | `'in 2 days'`                                                                  |

### Common Use-Cases and Examples:
The following section stands to describe common use-cases. Assuming that there are no overides provided over the `default` keys, the common specification parts (properties) like: `complete_oauth_server_input_specification` and `complete_oauth_server_output_specification` remain unchanged

  <details>
      <summary>Example Common Advanced Auth parts</summary>

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
  </details>

#### Case A: OAuth Flow returns the `access_token` only
When the `access_token` is the only key expected after the successful `OAuth2.0` authentication

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123"
}
```
  </details>

##### Case A-1: OAuth Flow returns the nested `access_token` only, under the `data` property

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>

```json
{
  "data": {
    "access_token": "YOUR_ACCESS_TOKEN_123"
  }
}
```
  </details>


#### Case B: OAuth Flow returns the `refresh_token` only
When the `refresh_token` is the only key expected after the successful `OAuth2.0` authentication

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>

```json
{
  "refresh_token": "YOUR_ACCESS_TOKEN_123"
}
```
  </details>

#### Case C: OAuth Flow returns the `access_token` and the `refresh_token`
When the `access_token` and the `refresh_token` are the only keys expected after the successful `OAuth2.0` authentication

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123"
}
```
  </details>

##### Case C-1: OAuth Flow returns the `access_token` and the `refresh_token` nested under the `data` property and each key is nested inside the dedicated placeholder

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>

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
  </details>

#### Case D: OAuth Flow returns the `access_token` and the `refresh_token` is a `one-time-usage` key
In this example we expect the `refresh_token` key expires alongside with the `access_token` and should be exhanged altogether, having the new pair of keys in response. The `token_expiry_date` is the property that holds the `date-time` value of when the `access_token` should be expired

  <details>
      <summary>Example Declarative OAuth Specification</summary>

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

  # Other common properties are omitted, see the `More common use-cases` description
```
  </details>

  <details>
      <summary>Example `path_in_oauth_response`</summary>  

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_123",
  "refresh_token": "YOUR_REFRESH_TOKEN_123",
  "expires_in": 7200
}
```
  </details>


## Partial OAuth (legacy)

The partial OAuth flow is a simpler flow that allows you to use an existing access (or refresh) token to authenticate with the API.

The catch is that the user needs to implement the start of the OAuth flow manually to obtain the `access_token` and the `refresh_token` and pass them to the connector as a part of the `config` object.

This method is supported through the `OAuthAuthenticator`, which requires the following parameters:

- `token_refresh_endpoint`: The endpoint to refresh the access token
- `client_id`: The client id
- `client_secret`: The client secret
- `refresh_token`: The token used to refresh the access token
- `scopes` (Optional): The scopes to request. Default: Empty list
- `token_expiry_date` (Optional): The access token expiration date formatted as RFC-3339 ("%Y-%m-%dT%H:%M:%S.%f%z")
- `access_token_name` (Optional): The field to extract access token from in the response. Default: "access_token".
- `expires_in_name` (Optional): The field to extract expires_in from in the response. Default: "expires_in"
- `refresh_request_body` (Optional): The request body to send in the refresh request. Default: None
- `grant_type` (Optional): The parameter specified grant_type to request access_token. Default: "refresh_token"

<details>
  <summary>Example Schema</summary>

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
    refresh_token_updater:
        title: Token Updater
        description: When the token updater is defined, new refresh tokens, access tokens and the access token expiry date are written back from the authentication response to the config object. This is important if the refresh token can only used once.
        properties:
          refresh_token_name:
            title: Refresh Token Property Name
            description: The name of the property which contains the updated refresh token in the response from the token refresh endpoint.
            type: string
            default: "refresh_token"
          access_token_config_path:
            title: Config Path To Access Token
            description: Config path to the access token. Make sure the field actually exists in the config.
            type: array
            items:
              type: string
            default: ["credentials", "access_token"]
          refresh_token_config_path:
            title: Config Path To Refresh Token
            description: Config path to the access token. Make sure the field actually exists in the config.
            type: array
            items:
              type: string
            default: ["credentials", "refresh_token"]
```
  </details>

  <details>
      <summary>Example Authenticator</summary>

```yaml
authenticator:
  type: "OAuthAuthenticator"
  token_refresh_endpoint: "https://api.searchmetrics.com/v4/token"
  client_id: "{{ config['api_key'] }}"
  client_secret: "{{ config['client_secret'] }}"
  refresh_token: ""
```
  </details>

For more information see [OAuthAuthenticator Reference](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/reference#/definitions/OAuthAuthenticator)
