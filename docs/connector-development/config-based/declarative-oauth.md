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

TODO: Explain high-level concepts, when to use Declarative OAuth vs custom implementation, and the core workflow of how it processes OAuth configurations.

## Configuration Fields

TODO: Document each field in the oauth_connector_input_specification schema, explaining their purpose, requirements, and behavior. Include code examples.

### Required Fields
TODO: Document mandatory fields like consent_url, access_token_url

### Optional Fields
TODO: Document optional configuration like custom keys, headers, params

## Available Template Variables

TODO: Create comprehensive table of all template variables available for string interpolation, their default values, and usage examples.

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

Example: `https://yourconnectorservice.com/oauth/consent?client_id=YOUR_CLIENT_ID_123&redirect_uri=cloud.airbyte.com&state=some_random_state_string`

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
diff --git a/docs/connector-development/config-based/current_example.yml b/docs/connector-development/config-based/current_example.yml
index e4d1ddd655..f7d69fd182 100644
--- a/docs/connector-development/config-based/current_example.yml
+++ b/docs/connector-development/config-based/current_example.yml
@@ -38,6 +38,14 @@ definitions:
   base_requester:
     type: HttpRequester
     url_base: https://pokeapi.co
+    authenticator:
+      type: OAuthAuthenticator
+      refresh_request_body: {}
+      client_id: "{{ config[\"client_id\"] }}"
+      client_secret: "{{ config[\"client_secret\"] }}"
+      access_token_value: "{{ config[\"client_access_token\"] }}"

 streams:
   - $ref: "#/definitions/streams/moves"
@@ -47,9 +55,85 @@ spec:
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
+          redirect_uri }}&state={{ state }}
+        access_token_url: >-
+          https://yourconnectorservice.com/oauth/token?client_id={{client_id_value}}&client_secret={{client_secret_value}}&code={{auth_code_value}}
+        extract_output:
+          - access_token
+        access_token_headers: {}
+        access_token_params: {}
+      complete_oauth_output_specification:
+        required:
+          - access_token
+        properties:
+          access_token:
+            type: string
+            path_in_connector_config:
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

 schemas:
   moves:
@@ -86,4 +170,3 @@ schemas:
               type:
                 - string
                 - "null"
-

```

### Advanced Case: access token is returned in a different or nested field
Now imagine that the OAuth flow is updated so that the access token returned by `/oauth/token` is in a non standard / nested field. Specifically, the response is now:
```json
{
  "data": {
    "super_duperaccess_token": "YOUR_ACCESS_TOKEN_123"
  }
}
```

#### Example Declarative OAuth Change
```diff

```

### Query Parameters
TODO: Demonstrate adding custom query parameters and using oauth_user_input_from_connector_config_specification

### Authorization Headers
TODO: Show how to add custom auth headers with access_token_headers

### Complete Example with Refresh Flow
TODO: Show a complete production example incorporating all features including refresh token support

## Best Practices

TODO: Document recommended patterns, common pitfalls to avoid, and security considerations.

## Troubleshooting

TODO: Add common issues and their solutions, debugging tips, and how to validate configurations.

# Declarative OAuth (experimental)
This is an experimental feature that allows you to configure OAuth authentication via a connectors spec output.

This feature is available for all connectors and has support in both our CDK and Connector Builder.

## Overview
This feature is primarily concerned with the `OAuthConfigSpecification` type as defined in the [protocol](https://github.com/airbytehq/airbyte-protocol/blob/d14cffb8123a8debe2d1c9c32c466f127ac1fb19/protocol-models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L658C7-L658C42) and made available for use in the connector `spec` at `advanced_auth.oauth_config`.



## Progressive Example

### Simple OAuth with no overrides

